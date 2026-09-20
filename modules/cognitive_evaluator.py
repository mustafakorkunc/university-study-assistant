from google import genai
from google.genai import types
import json
import config

def generate_exam_questions(context, api_key, num_questions=3):
    client = genai.Client(api_key=api_key)
    
    prompt = (
        f"Generate {num_questions} free-response exam questions based on the context. "
        "Categorize each question according to Bloom's Revised Taxonomy (Remember, Understand, Apply, Analyze, Evaluate, Create). "
        "Return a JSON array of objects with 'question' and 'bloom_level'.\n\n"
        f"Context:\n{context}"
    )
    try:
        response = client.models.generate_content(
            model=config.MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(e)
        return []

def evaluate_response(question, student_answer, context, api_key):
    client = genai.Client(api_key=api_key)
    prompt = (
        "Evaluate the student's free-text response to the question using the provided context as the source of truth. Apply an academic rubric.\n"
        "Return a JSON object with:\n"
        "- 'score': Integer from 0 to 100 representing Factual Accuracy.\n"
        "- 'reasoning_quality': A brief comment on their reasoning quality.\n"
        "- 'misconceptions': Specific Diagnosis identifying any false premises in the student's logic.\n"
        "- 'socratic_guidance': Socratic follow-up guidance without leaking the direct final answer.\n\n"
        f"Context: {context}\n"
        f"Question: {question}\n"
        f"Student Answer: {student_answer}"
    )
    
    try:
        response = client.models.generate_content(
            model=config.MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(e)
        return {"error": str(e)}
