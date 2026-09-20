from google import genai
from google.genai import types
from pydantic import BaseModel, Field, field_validator
import json
import config

class ExamQuestion(BaseModel):
    question: str = Field(description="The actual exam question.")
    bloom_level: str = Field(description="Must be one of: Remember, Understand, Apply, Analyze, Evaluate, Create")
    primary_concept: str = Field(description="The primary learning concept this question targets.")

    @field_validator('bloom_level')
    def validate_bloom(cls, v):
        allowed = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
        if v not in allowed:
            raise ValueError(f"Invalid Bloom Level: {v}")
        return v

class ExamQuestionList(BaseModel):
    questions: list[ExamQuestion]

class EvaluationResponse(BaseModel):
    score: int = Field(description="Score from 0 to 100.")
    reasoning_quality: str = Field(description="Explanation of why the score was given.")
    concepts_involved: list[str] = Field(description="List of concepts involved in the student's answer.")
    primary_concept: str = Field(description="The main concept tested.")
    misconception: str = Field(description="Specific misconception detected. Return 'None' if perfectly correct.")
    misconception_category: str = Field(description="Category of misconception. Return 'None' if perfectly correct. Example: 'factual_error', 'energy_source_confusion'.")
    socratic_guidance: str = Field(description="Socratic hint to help them if they failed.")

    @field_validator('score')
    def validate_score(cls, v):
        if not (0 <= v <= 100):
            raise ValueError("Score must be between 0 and 100")
        return v

from prompts.question_generator import QUESTION_GENERATOR_PROMPT
from prompts.evaluator import EVALUATOR_PROMPT

def generate_exam_questions(context, api_key, num_questions=3, target_concept=None):
    client = genai.Client(api_key=api_key)
    
    prompt = QUESTION_GENERATOR_PROMPT.format(
        context=context,
        target_concept=target_concept or "None specified"
    )
    prompt += f"\nGenerate {num_questions} questions."
    
    try:
        response = client.models.generate_content(
            model=config.LLM_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExamQuestionList,
                temperature=0.3
            )
        )
        data = ExamQuestionList.model_validate_json(response.text)
        return data.questions
    except Exception as e:
        print(f"Error generating questions: {e}")
        return []

def evaluate_response(question, student_answer, context, api_key):
    client = genai.Client(api_key=api_key)
    prompt = EVALUATOR_PROMPT.format(
        context=context,
        question=question,
        student_answer=student_answer
    )
    
    try:
        response = client.models.generate_content(
            model=config.LLM_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=EvaluationResponse,
                temperature=0.1
            )
        )
        data = EvaluationResponse.model_validate_json(response.text)
        return data
    except Exception as e:
        print(f"Error evaluating response: {e}")
        return None

class GeneratedFlashcard(BaseModel):
    front: str
    back: str
    concept: str

class FlashcardList(BaseModel):
    cards: list[GeneratedFlashcard]

def generate_flashcards_for_concept(course_id, concept_id, count, difficulty, card_type, db, api_key):
    from modules.db import Concept
    from modules.rag_engine import RetrievalService
    
    concept = db.query(Concept).get(concept_id)
    if not concept: return []
    
    rs = RetrievalService(api_key)
    evidence = rs.retrieve(f"Core concepts and definitions regarding {concept.label}", course_id, db, top_k=5)
    context = "\n".join([c["text"] for c in evidence])
    
    prompt = f"""
    Context: {context}
    
    Generate {count} flashcards about the concept '{concept.label}'.
    Difficulty: {difficulty}
    Card Type: {card_type}
    
    The front should be a clear question or prompt. The back should be the answer.
    """
    
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model=config.LLM_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=FlashcardList,
                temperature=0.3
            )
        )
        data = FlashcardList.model_validate_json(response.text)
        return data.cards
    except Exception as e:
        print(f"Flashcard generation error: {e}")
        return []
