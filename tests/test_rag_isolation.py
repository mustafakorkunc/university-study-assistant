import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from modules.db import Base, Course, Document, Chunk
from modules.rag_engine import RetrievalService
from unittest.mock import MagicMock
import json

@pytest.fixture
def test_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_course_isolation(test_db):
    # Setup Course A (Physics)
    course_a = Course(user_id=1, title="Physics")
    test_db.add(course_a)
    test_db.commit()
    
    doc_a = Document(course_id=course_a.id, filename="physics.pdf")
    test_db.add(doc_a)
    test_db.commit()
    
    chunk_a = Chunk(document_id=doc_a.id, content="Gravity is 9.8 m/s^2", embedding=json.dumps([0.1]*768))
    test_db.add(chunk_a)
    test_db.commit()

    # Setup Course B (History)
    course_b = Course(user_id=1, title="History")
    test_db.add(course_b)
    test_db.commit()
    
    doc_b = Document(course_id=course_b.id, filename="history.pdf")
    test_db.add(doc_b)
    test_db.commit()
    
    chunk_b = Chunk(document_id=doc_b.id, content="George Washington was the first president.", embedding=json.dumps([0.9]*768))
    test_db.add(chunk_b)
    test_db.commit()

    # Mock the RetrievalService Gemini Client
    rs = RetrievalService(api_key="mock")
    # Mocking the embedding to match History just to prove it won't pull Physics
    mock_response = MagicMock()
    mock_response.embeddings = [MagicMock(values=[0.9]*768)]
    rs.client.models.embed_content = MagicMock(return_value=mock_response)

    # Search in Course A (Physics) for "Washington"
    results = rs.retrieve("Washington", course_a.id, test_db)
    
    # We should NEVER see chunk_b because it belongs to Course B
    for r in results:
        assert "Washington" not in r["text"]
        assert r["document_id"] == doc_a.id

    # Search in Course B (History) for "Washington"
    results_b = rs.retrieve("Washington", course_b.id, test_db)
    assert len(results_b) > 0
    assert "Washington" in results_b[0]["text"]
