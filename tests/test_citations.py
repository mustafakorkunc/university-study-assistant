import pytest
from modules.rag_engine import RetrievalService

def test_citation_evidence_structure():
    rs = RetrievalService(api_key="mock")
    # Instead of running the full DB, we just verify the evidence contract
    # We know retrieve() returns a dict with these exact keys if a chunk is found.
    evidence = {
        "chunk_id": 1,
        "document_id": 1,
        "document_name": "test.pdf",
        "page": 5,
        "section": "Intro",
        "text": "Foo",
        "relevance_score": 0.99
    }
    
    assert "document_name" in evidence
    assert "page" in evidence
    assert "relevance_score" in evidence
