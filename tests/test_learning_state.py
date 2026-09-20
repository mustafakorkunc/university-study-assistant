import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from modules.db import Base, Course, Concept, Flashcard, QuestionAttempt, Misconception, FlashcardReviewEvent
from modules.adaptive_learning import get_next_best_action, get_course_learning_state, get_concept_state

@pytest.fixture
def test_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

def test_mastery_calculation(test_db):
    course = Course(title="Test Course", user_id=1)
    test_db.add(course)
    test_db.commit()
    
    concept = Concept(course_id=course.id, label="Photosynthesis", definition="Process")
    test_db.add(concept)
    test_db.commit()
    
    # 1. No evidence
    state = get_concept_state(1, course.id, concept.id, test_db)
    assert state["mastery_score"] == 0.5  # Sigmoid of 0
    
    # 2. Positive evidence
    fc = Flashcard(course_id=course.id, concept_id=concept.id, front="Q", back="A")
    test_db.add(fc)
    test_db.commit()
    
    rev = FlashcardReviewEvent(flashcard_id=fc.id, quality=5, previous_interval=1, new_interval=6)
    test_db.add(rev)
    test_db.commit()
    
    state = get_concept_state(1, course.id, concept.id, test_db)
    assert state["mastery_score"] > 0.5
    
    # 3. Active Misconception
    misc = Misconception(course_id=course.id, concept_id=concept.id, category="factual_error", description="Oops")
    test_db.add(misc)
    test_db.commit()
    
    state = get_concept_state(1, course.id, concept.id, test_db)
    assert state["mastery_score"] < 0.5

def test_next_best_action(test_db):
    course = Course(title="Test Course", user_id=1)
    test_db.add(course)
    test_db.commit()
    
    # Due cards trigger REVIEW
    for i in range(15):
        fc = Flashcard(course_id=course.id, front="Q", back="A", next_review=datetime.utcnow() - timedelta(days=1))
        test_db.add(fc)
    test_db.commit()
    
    action = get_next_best_action(1, course.id, test_db)
    assert action["action"] == "REVIEW"

def test_course_learning_state(test_db):
    course = Course(title="Test Course", user_id=1)
    test_db.add(course)
    test_db.commit()
    
    concept = Concept(course_id=course.id, label="C", definition="D")
    test_db.add(concept)
    test_db.commit()
    
    readiness = get_course_learning_state(1, course.id, test_db)
    assert "score" in readiness
    assert "status" in readiness
