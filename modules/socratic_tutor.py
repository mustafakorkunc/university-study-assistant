from google import genai
from google.genai import types
import config

def get_socratic_response(user_input, chat_history, document_context):
    """
    Generates a response acting as a Socratic tutor.
    """
    if not config.GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY is not set in the environment variables."
        
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    
    system_instruction = (
        "You are a Socratic tutor. Your goal is to help the student learn by asking guiding questions "
        "and providing hints, rather than giving the direct answer immediately. "
        "Use the provided document context if relevant to the student's question."
    )
    
    context_prompt = f"Document Context:\n{document_context}\n\nStudent: {user_input}" if document_context else f"Student: {user_input}"
    
    contents = []
    for msg in chat_history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])]
            )
        )
    
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=context_prompt)]
        )
    )

    try:
        response = client.models.generate_content(
            model=config.MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
            )
        )
        return response.text
    except Exception as e:
         return f"Error communicating with Gemini API: {e}"
