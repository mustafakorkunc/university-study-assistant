import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from modules.db import Base, Course, Concept, Flashcard, QuestionAttempt, Misconception, FlashcardReviewEvent
from modules.adaptive_learning import get_next_best_action, get_concept_state

@pytest.fixture
def test_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

def test_actual_learning_loop(test_db):
    # 0. Student starts with no evidence
    course = Course(title="Biology", user_id=1)
    test_db.add(course)
    test_db.commit()
    
    concept = Concept(course_id=course.id, label="Photosynthesis", definition="...")
    test_db.add(concept)
    test_db.commit()
    
    # Assert initial state
    state = get_concept_state(1, course.id, concept.id, test_db)
    assert state["mastery_score"] == 0.5
    
    # 1. Student fails Photosynthesis question
    attempt = QuestionAttempt(course_id=course.id, concept_id=concept.id, question="What is it?", student_answer="Fire", score=0)
    test_db.add(attempt)
    
    # 2. Misconception recorded
    misc = Misconception(course_id=course.id, concept_id=concept.id, category="factual_error", description="Thinks it's fire")
    test_db.add(misc)
    test_db.commit()
    
    # 3. Mastery falls
    state = get_concept_state(1, course.id, concept.id, test_db)
    assert state["mastery_score"] < 0.5
    
    # 4. Next-best-action becomes misconception repair
    action = get_next_best_action(1, course.id, test_db)
    assert action["action"] == "FIX_MISCONCEPTION"
    assert action["concept"] == "Photosynthesis"
    
    # 5. Student completes repair (resolves misconception)
    misc.status = "resolved"
    test_db.commit()
    
    # 6. Student passes recall card
    fc = Flashcard(course_id=course.id, concept_id=concept.id, front="Q", back="A", interval=6)
    test_db.add(fc)
    test_db.commit()
    
    rev = FlashcardReviewEvent(flashcard_id=fc.id, quality=5, previous_interval=1, new_interval=6)
    test_db.add(rev)
    test_db.commit()
    
    # 7. Mastery rises
    state = get_concept_state(1, course.id, concept.id, test_db)
    assert state["mastery_score"] > 0.5
    
    # 8. Forgetting risk scheduled
    assert state["forgetting_risk"] >= 0.0
    
    # 9. Next study action changes
    action = get_next_best_action(1, course.id, test_db)
    assert action["action"] != "FIX_MISCONCEPTION"
