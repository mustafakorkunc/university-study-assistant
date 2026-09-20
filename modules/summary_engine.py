from google import genai
from google.genai import types
import config

def generate_summary(document_context):
    """
    Generates a structured summary and cheat-sheet from the document context.
    """
    if not config.GEMINI_API_KEY:
         return "Error: GEMINI_API_KEY is not set."
         
    if not document_context:
         return "No document context provided. Please upload a document first."
         
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    
    prompt = (
        "Based on the following document context, create a comprehensive yet concise 'Cheat Sheet'.\n"
        "Include the following sections:\n"
        "1. Executive Summary\n"
        "2. Key Terms & Definitions\n"
        "3. Core Concepts / Formulas\n\n"
        f"Document Context:\n{document_context}"
    )

    try:
        response = client.models.generate_content(
            model=config.MODEL_NAME,
            contents=prompt,
             config=types.GenerateContentConfig(
                temperature=0.2,
            )
        )
        return response.text
    except Exception as e:
        return f"Error generating summary: {e}"
