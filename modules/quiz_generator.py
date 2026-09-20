from google import genai
from google.genai import types
import config
import json

def generate_quiz(document_context, num_questions=5):
    """
    Generates a multiple-choice quiz based on the document context.
    Returns a list of dictionaries containing questions, options, and answers.
    """
    if not config.GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY is not set."}
        
    if not document_context:
        return {"error": "No document context provided. Please upload a document first."}
        
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    
    prompt = (
        f"Based on the following text, generate a {num_questions}-question multiple-choice quiz.\n"
        "Return ONLY a valid JSON array of objects. Each object should have the following structure:\n"
        "{\n"
        '  "question": "The question text",\n'
        '  "options": ["Option A", "Option B", "Option C", "Option D"],\n'
        '  "answer": "The exact text of the correct option",\n'
        '  "explanation": "Brief explanation of why this is the correct answer"\n'
        "}\n\n"
        f"Text Context:\n{document_context}"
    )

    try:
        response = client.models.generate_content(
            model=config.MODEL_NAME,
            contents=prompt,
             config=types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {"error": "Failed to parse quiz format from AI response."}
    except Exception as e:
        return {"error": f"Error generating quiz: {e}"}
