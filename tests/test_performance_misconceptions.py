import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from modules.db import Base, Course, Concept, Misconception
from modules.adaptive_learning import get_recurring_misconceptions

@pytest.fixture
def test_db():
    engine = create_engine('sqlite:///:memory:', echo=True) # Echo true to see queries
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

def test_get_recurring_misconceptions_performance(test_db, benchmark):
    course = Course(title="Biology", user_id=1)
    test_db.add(course)
    test_db.commit()

    # Create 100 concepts and 100 active misconceptions
    for i in range(100):
        concept = Concept(course_id=course.id, label=f"Concept {i}", definition="...")
        test_db.add(concept)
        test_db.flush()

        misc = Misconception(course_id=course.id, concept_id=concept.id, category="error", description=f"desc {i}")
        test_db.add(misc)

    test_db.commit()

    # Disable echo during benchmark to avoid stdout clutter
    test_db.bind.echo = False

    def run_query():
        return get_recurring_misconceptions(1, course.id, test_db)

    # Benchmark the function
    result = benchmark(run_query)
    assert len(result) == 100
