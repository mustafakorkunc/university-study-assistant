import pytest
from modules.adaptive_learning import get_next_best_action
from modules.db import Course, Concept, Flashcard, Misconception, MistakeLog, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def test_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_exam_adaptation(test_db):
    course = Course(user_id=1, title="Test")
    test_db.add(course)
    test_db.commit()
    
    concept = Concept(course_id=course.id, label="Photosynthesis", definition="Process")
    test_db.add(concept)
    test_db.commit()
    
    # Repeated mistakes should force the exam to adapt by focusing on this concept
    m1 = Misconception(course_id=course.id, concept_id=concept.id, category="factual_error", description="Photosynthesis error")
    test_db.add(m1)
    test_db.commit()
    
    action = get_next_best_action(1, course.id, test_db)
    
    # The Learning Engine determines the exam target
    assert action["action"] == "FIX_MISCONCEPTION"
    assert action["concept"] == "Photosynthesis"
