import os
import re
import json
from pypdf import PdfReader
from google import genai
from rank_bm25 import BM25Okapi
import numpy as np
import config
from collections import defaultdict
from sqlalchemy.orm import Session
from modules.db import Chunk, Document

def chunk_text(text, page_number):
    chunks = []
    # Improved splitting to keep boundaries better
    paragraphs = re.split(r'\n(?=\s*[A-Z0-9])|\n\s*\n', text)
    current_heading = "General Context"
    
    for p in paragraphs:
        p = p.strip()
        if not p or len(p) < 15: # Ignore very short artifacts
            continue
        # If it looks like a heading
        if len(p) < 80 and not p.endswith('.') and not p.endswith(','):
            current_heading = p
        else:
            chunks.append({
                "content": p,
                "page_number": page_number,
                "section_heading": current_heading
            })
    return chunks

def extract_pdf(file_path, start_page=None, end_page=None):
    reader = PdfReader(file_path)
    all_chunks = []
    
    total_pages = len(reader.pages)
    
    start_idx = max(0, start_page - 1) if start_page is not None else 0
    end_idx = min(total_pages, end_page) if end_page is not None else total_pages
    
    for i in range(start_idx, end_idx):
        page = reader.pages[i]
        text = page.extract_text()
        if text:
            all_chunks.extend(chunk_text(text, i + 1))
    return all_chunks

def extract_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return chunk_text(text, 1)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10)

class RetrievalService:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def retrieve(self, query: str, course_id: int, db: Session, top_k: int = config.TOP_K_RETRIEVAL):
        """
        Retrieves the most relevant chunks strictly for the given course_id.
        """
        chunks = db.query(Chunk).join(Document).filter(Document.course_id == course_id).all()
        if not chunks:
            return []
            
        corpus = [c.content.lower().split() for c in chunks]
        bm25 = BM25Okapi(corpus)
        
        # 1. Lexical retrieval
        tokenized_query = query.lower().split()
        bm25_scores = bm25.get_scores(tokenized_query)
        
        # 2. Semantic retrieval
        q_emb = None
        try:
            resp = self.client.models.embed_content(
                model=config.EMBEDDING_MODEL,
                contents=query
            )
            q_emb = resp.embeddings[0].values
        except Exception as e:
            print(f"Query embedding failed: {e}. Falling back to lexical-only retrieval.")
            
        semantic_scores = {}
        if q_emb:
            for chunk in chunks:
                if chunk.embedding:
                    try:
                        c_emb = json.loads(chunk.embedding) if isinstance(chunk.embedding, str) else chunk.embedding
                        if sum(abs(v) for v in c_emb) > 1e-5 and sum(abs(v) for v in q_emb) > 1e-5:
                            semantic_scores[chunk.id] = cosine_similarity(q_emb, c_emb)
                    except:
                        pass
        
        # 3. Reciprocal Rank Fusion (RRF)
        bm25_ranks = np.argsort(bm25_scores)[::-1]
        vector_scores = [semantic_scores.get(c.id, 0.0) for c in chunks]
        vector_ranks = np.argsort(vector_scores)[::-1]
        
        rrf_scores = defaultdict(float)
        k_fusion = config.RRF_K
        
        for rank, doc_idx in enumerate(bm25_ranks):
            rrf_scores[doc_idx] += 1 / (k_fusion + rank + 1)
            
        for rank, doc_idx in enumerate(vector_ranks):
            rrf_scores[doc_idx] += 1 / (k_fusion + rank + 1)
            
        sorted_indices = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        
        results = []
        for idx in sorted_indices:
            c = chunks[idx]
            if rrf_scores[idx] < config.RRF_THRESHOLD:
                continue
                
            evidence = {
                "chunk_id": c.id,
                "document_id": c.document_id,
                "document_name": c.document.filename,
                "page": c.page_number,
                "section": c.section_heading,
                "text": c.content,
                "relevance_score": rrf_scores[idx]
            }
            results.append(evidence)
            if len(results) >= top_k:
                break
                
        return results

def get_retrieval_service(api_key):
    return RetrievalService(api_key=api_key)
