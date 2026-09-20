import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    courses = relationship("Course", back_populates="user", cascade="all, delete-orphan")

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="courses")
    documents = relationship("Document", back_populates="course", cascade="all, delete-orphan")
    flashcards = relationship("Flashcard", back_populates="course", cascade="all, delete-orphan")
    concepts = relationship("Concept", back_populates="course", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="course", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    filename = Column(String, nullable=False)
    status = Column(String, default="processing") # processing, ready, error
    word_count = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    course = relationship("Course", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = 'chunks'
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    page_number = Column(Integer)
    section_heading = Column(String)
    content = Column(Text, nullable=False)
    # Storing embeddings locally in SQLite for now (can use JSON or blob).
    embedding = Column(Text, nullable=True) 
    
    document = relationship("Document", back_populates="chunks")

class Concept(Base):
    __tablename__ = 'concepts'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    label = Column(String, nullable=False)
    definition = Column(Text, nullable=False)
    
    # Adaptive Learning Engine Estimates
    mastery_score = Column(Float, default=0.0)
    confidence = Column(Float, default=0.5)
    difficulty = Column(Float, default=0.5)
    last_seen = Column(DateTime, default=datetime.utcnow)
    
    course = relationship("Course", back_populates="concepts")

class Flashcard(Base):
    __tablename__ = 'flashcards'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    concept_id = Column(Integer, ForeignKey('concepts.id'), nullable=True)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    source_citation = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # SM-2 fields
    ease_factor = Column(Float, default=2.5)
    interval = Column(Integer, default=0)
    repetitions = Column(Integer, default=0)
    next_review = Column(DateTime, default=datetime.utcnow)
    
    course = relationship("Course", back_populates="flashcards")
    concept = relationship("Concept")

class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    topic = Column(String, default="General")
    history_json = Column(Text, default="[]")
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    course = relationship("Course", back_populates="chat_sessions")

# --- Learning Event Models (Phase 4) ---

class QuestionAttempt(Base):
    __tablename__ = 'question_attempts'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    concept_id = Column(Integer, ForeignKey('concepts.id'), nullable=True)
    question = Column(Text, nullable=False)
    student_answer = Column(Text, nullable=False)
    score = Column(Integer, nullable=False)
    bloom_level = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    misconception_id = Column(Integer, ForeignKey('misconceptions.id'), nullable=True)

class Misconception(Base):
    __tablename__ = 'misconceptions'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    concept_id = Column(Integer, ForeignKey('concepts.id'), nullable=True)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="active") # active or resolved

class FlashcardReviewEvent(Base):
    __tablename__ = 'flashcard_review_events'
    id = Column(Integer, primary_key=True)
    flashcard_id = Column(Integer, ForeignKey('flashcards.id'), nullable=False)
    quality = Column(Integer, nullable=False) # 0-5
    timestamp = Column(DateTime, default=datetime.utcnow)
    previous_interval = Column(Integer, nullable=False)
    new_interval = Column(Integer, nullable=False)

# Keep MistakeLog for legacy UI until fully migrated
class MistakeLog(Base):
    __tablename__ = 'mistake_logs'
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    question = Column(Text, nullable=False)
    student_answer = Column(Text, nullable=False)
    misconception = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ConceptEdge(Base):
    __tablename__ = 'concept_edges'
    id = Column(Integer, primary_key=True)
    source_concept_id = Column(Integer, ForeignKey('concepts.id'), nullable=False)
    target_concept_id = Column(Integer, ForeignKey('concepts.id'), nullable=False)
    relationship_type = Column(String, nullable=False) # PREREQUISITE, RELATED_TO, etc
    evidence = Column(Text, nullable=True)

engine = create_engine('sqlite:///study_engine.db', connect_args={'check_same_thread': False})

# Run migrations programmatically for Streamlit Cloud
import os
import sys

if not os.environ.get("ALEMBIC_CONTEXT") and "alembic" not in sys.argv[0]:
    try:
        import alembic.config
        alembic_args = ['--raiseerr', 'upgrade', 'head']
        alembic.config.main(argv=alembic_args)
    except Exception as e:
        print(f"Migration failed or not required: {e}")

SessionLocal = sessionmaker(bind=engine, autoflush=False)

def get_session():
    return SessionLocal()

def update_sm2(flashcard, quality):
    """
    SuperMemo-2 Algorithm
    quality: 0-5 (0=blackout, 5=perfect)
    """
    if quality < 3:
        flashcard.repetitions = 0
        flashcard.interval = 1
    else:
        if flashcard.repetitions == 0:
            flashcard.interval = 1
        elif flashcard.repetitions == 1:
            flashcard.interval = 6
        else:
            flashcard.interval = round(flashcard.interval * flashcard.ease_factor)
        
        flashcard.repetitions += 1
        
    flashcard.ease_factor = flashcard.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if flashcard.ease_factor < 1.3:
        flashcard.ease_factor = 1.3
        
    flashcard.next_review = datetime.utcnow() + timedelta(days=flashcard.interval)
