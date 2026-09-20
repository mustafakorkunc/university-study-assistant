import os
import streamlit as st
from typing import Optional

def get_gemini_api_key() -> Optional[str]:
    """Retrieve the Gemini API key from environment, secrets, or session state."""
    # 1. Check session state first
    if "current_api_key" in st.session_state and st.session_state.current_api_key:
        return st.session_state.current_api_key
        
    # 2. Check Streamlit Secrets
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
        
    # 3. Check OS Environment
    env_key = os.getenv("GEMINI_API_KEY")
    if env_key:
        return env_key
        
    return None

class AppConfig:
    EMBEDDING_MODEL: str = "text-embedding-004"
    LLM_MODEL: str = "gemini-2.5-flash"
    TOP_K_RETRIEVAL: int = 5
    RRF_K: int = 60
    RRF_THRESHOLD: float = 0.01

    @classmethod
    def get_api_key(cls) -> Optional[str]:
        return get_gemini_api_key()

config = AppConfig()
