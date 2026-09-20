import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import json

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    filename = Column(String, unique=True, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = 'chunks'
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    page_number = Column(Integer)
    section_heading = Column(String)
    content = Column(Text, nullable=False)
    
    document = relationship("Document", back_populates="chunks")

class Flashcard(Base):
    __tablename__ = 'flashcards'
    id = Column(Integer, primary_key=True)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # SM-2 fields
    ease_factor = Column(Float, default=2.5)
    interval = Column(Integer, default=0)
    repetitions = Column(Integer, default=0)
    next_review = Column(DateTime, default=datetime.utcnow)

engine_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'study_engine.db')
engine = create_engine(f'sqlite:///{engine_path}')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

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
