from google import genai
import os
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
try:
    resp = client.models.embed_content(
        model="gemini-embedding-2",
        contents=["?? Hello world", "Normal text"]
    )
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
