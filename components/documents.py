import streamlit as st
import os
import tempfile
import config
from modules.db import Document, Chunk, Flashcard
from modules.rag_engine import extract_pdf, extract_txt

def render(db, course_id):
    if not course_id:
        st.warning("NO ACTIVE CONTEXT. PLEASE SELECT A COURSE.")
        return
        
    st.header("◈ DOCUMENT INGESTION")
    st.caption("UPLOAD RAW DATA FOR NEURAL PROCESSING")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Upload Material")
        uploaded_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])
        
        if uploaded_file is not None:
            max_size_mb = 10
            if uploaded_file.size > max_size_mb * 1024 * 1024:
                st.error(f"File exceeds {max_size_mb}MB limit.")
                st.stop()
                
            valid_extensions = [".pdf", ".txt"]
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            if file_ext not in valid_extensions:
                st.error("Invalid file format. Only PDF and TXT are allowed.")
                st.stop()
                
            start_page = None
            end_page = None
            if file_ext == ".pdf":
                st.info("💡 Large textbook? Specify a page range to extract just a specific chapter and avoid rate limits.")
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    start_page = st.number_input("Start Page (Optional)", min_value=1, value=None, placeholder="e.g., 15")
                with col_p2:
                    end_page = st.number_input("End Page (Optional)", min_value=1, value=None, placeholder="e.g., 45")
                
            if st.button("Process Document", type="primary"):
                import re
                safe_filename = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', uploaded_file.name)
                
                # Deduplication
                existing = db.query(Document).filter_by(course_id=course_id, filename=safe_filename).first()
                if existing:
                    st.error("A document with this name already exists in this course.")
                    st.stop()
                    
                with st.spinner(f"Ingesting {safe_filename}..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        temp_path = tmp_file.name
                    
                    db_doc = None
                    try:
                        db_doc = Document(course_id=course_id, filename=safe_filename, status="INDEXING")
                        db.add(db_doc)
                        db.commit()
                        
                        extracted_chunks = []
                        if file_ext == ".pdf":
                            extracted_chunks = extract_pdf(temp_path, start_page, end_page)
                        elif file_ext == ".txt":
                            extracted_chunks = extract_txt(temp_path)
                            
                        if not extracted_chunks:
                            raise ValueError("No text could be extracted from the document.")
                                
                        texts = [c["content"] for c in extracted_chunks]
                        from google import genai
                        client = genai.Client(api_key=st.session_state.current_api_key)
                        
                        batch_size = 50
                        import json
                        import time
                        
                        embeddings_successful = True
                        progress_text = "Generating semantic embeddings..."
                        my_bar = st.progress(0, text=progress_text)
                        
                        try:
                            total_batches = (len(texts) + batch_size - 1) // batch_size
                            for idx, i in enumerate(range(0, len(texts), batch_size)):
                                batch = texts[i:i+batch_size]
                                resp = client.models.embed_content(
                                    model=config.EMBEDDING_MODEL,
                                    contents=batch
                                )
                                for j, emb in enumerate(resp.embeddings):
                                    extracted_chunks[i+j]["embedding"] = json.dumps(emb.values)
                                    
                                my_bar.progress((idx + 1) / total_batches, text=f"Embedded {i+len(batch)} / {len(texts)} chunks...")
                                time.sleep(4.5) # Prevent Gemini Free Tier rate limits (15 RPM)
                        except Exception as emb_e:
                            my_bar.empty()
                            embeddings_successful = False
                            raise ValueError(f"Gemini API Error: {emb_e}")
                            
                        my_bar.empty()
                        
                        if not embeddings_successful:
                            raise ValueError("Semantic indexing failed. Document cannot be queried reliably.")
                            
                        total_words = 0
                        for c in extracted_chunks:
                            total_words += len(c["content"].split())
                            db_chunk = Chunk(
                                document_id=db_doc.id,
                                page_number=c["page_number"],
                                section_heading=c["section_heading"],
                                content=c["content"],
                                embedding=c.get("embedding")
                            )
                            db.add(db_chunk)
                        
                        db_doc.status = "READY"
                        db_doc.word_count = total_words
                        db.commit()
                        st.success(f"Processed {len(extracted_chunks)} chunks.")
                    except Exception as e:
                        db.rollback()
                        if db_doc and db_doc.id:
                            db_doc.status = "ERROR"
                            db.commit()
                        st.error(f"Failed to process document. Error: {str(e)}")
                        print(f"Ingest Error: {e}")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

    with col2:
        st.subheader("Your Documents")
        docs = db.query(Document).filter_by(course_id=course_id).all()
        if not docs:
            st.info("No documents uploaded yet.")
        for d in docs:
            with st.container():
                st.write(f"📄 **{d.filename}**")
                
                # Color code status
                color = "green" if d.status == "READY" else ("red" if d.status == "ERROR" else "orange")
                st.markdown(f"Status: <span style='color:{color}'>{d.status}</span> | Words: {d.word_count or 0}", unsafe_allow_html=True)
                
                if st.button("Delete", key=f"del_doc_{d.id}"):
                    db.delete(d)
                    db.commit()
                    st.rerun()
                st.divider()
