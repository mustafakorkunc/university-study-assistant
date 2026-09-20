import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from modules.db import Base, Flashcard, update_sm2

@pytest.fixture
def test_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_flashcard_learning_loop(test_db):
    fc = Flashcard(course_id=1, front="Q", back="A")
    test_db.add(fc)
    test_db.commit()
    
    # Simulate a perfect recall
    update_sm2(fc, 5)
    assert fc.interval == 1
    assert fc.ease_factor > 2.5
    
    # Simulate a blackout (complete fail)
    update_sm2(fc, 0)
    assert fc.interval == 1
    assert fc.ease_factor < 2.6  # Reduced
    
    # Assert next review is calculated
    assert fc.next_review > datetime.utcnow()
