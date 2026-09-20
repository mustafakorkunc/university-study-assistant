import pytest
from modules.rag_engine import chunk_text

def test_chunk_text_basic():
    text = "Heading\n\nThis is paragraph 1.\n\nThis is paragraph 2."
    chunks = chunk_text(text, 1)
    
    assert len(chunks) == 2
    assert chunks[0]["section_heading"] == "Heading"
    assert chunks[0]["content"] == "This is paragraph 1."
    assert chunks[1]["section_heading"] == "Heading"
    assert chunks[1]["content"] == "This is paragraph 2."
