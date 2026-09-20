import io
import re
from pypdf import PdfReader
from google import genai
from rank_bm25 import BM25Okapi
import numpy as np
import config

def chunk_text(text, page_number):
    chunks = []
    # Simplified structural chunking: split by paragraphs
    paragraphs = re.split(r'\n\s*\n', text)
    current_heading = "General Context"
    
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        # Heuristic for heading: short line, looks like title
        if len(p) < 80 and not p.endswith('.') and not p.endswith(','):
            current_heading = p
        else:
            chunks.append({
                "content": p,
                "page_number": page_number,
                "section_heading": current_heading
            })
    return chunks

def extract_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    all_chunks = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            all_chunks.extend(chunk_text(text, i + 1))
    return all_chunks

class HybridRAG:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.chunks = []
        self.corpus = []
        self.bm25 = None
        self.embeddings = []
    
    def ingest_chunks(self, chunks):
        self.chunks = chunks
        if not chunks:
            return
        self.corpus = [c["content"].lower().split() for c in chunks]
        self.bm25 = BM25Okapi(self.corpus)
        
        # Batch embed (simplified, handles rate limits by doing single calls if needed, 
        # but text-embedding-004 supports batching arrays)
        texts = [c["content"] for c in chunks]
        try:
            response = self.client.models.embed_content(
                model='text-embedding-004',
                contents=texts
            )
            self.embeddings = [e.values for e in response.embeddings]
        except Exception as e:
            print(f"Embedding error: {e}")
            self.embeddings = [np.zeros(768) for _ in texts]

    def search(self, query, top_k=5):
        if not self.chunks:
            return []
            
        # BM25 scores
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Vector scores
        try:
            q_emb = self.client.models.embed_content(
                model='text-embedding-004',
                contents=query
            ).embeddings[0].values
        except:
            q_emb = np.zeros(768)
            
        vector_scores = []
        for emb in self.embeddings:
            norm_q = np.linalg.norm(q_emb)
            norm_e = np.linalg.norm(emb)
            if norm_q == 0 or norm_e == 0:
                vector_scores.append(0.0)
            else:
                score = np.dot(q_emb, emb) / (norm_q * norm_e)
                vector_scores.append(score)
                
        # Reciprocal Rank Fusion (RRF)
        bm25_ranks = np.argsort(bm25_scores)[::-1]
        vector_ranks = np.argsort(vector_scores)[::-1]
        
        rrf_scores = np.zeros(len(self.chunks))
        k = 60
        for rank, doc_idx in enumerate(bm25_ranks):
            rrf_scores[doc_idx] += 1.0 / (k + rank + 1)
        for rank, doc_idx in enumerate(vector_ranks):
            rrf_scores[doc_idx] += 1.0 / (k + rank + 1)
            
        top_indices = np.argsort(rrf_scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append(self.chunks[idx])
        return results
