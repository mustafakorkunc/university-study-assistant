import streamlit as st
import config

def apply_cyber_theme():
    css = f"""
    <style>
    /* Global Backgrounds */
    .stApp {{
        background-color: {config.COLOR_BG};
        color: {config.COLOR_TEXT};
        font-family: 'Inter', sans-serif;
    }}
    .stAppHeader {{
        background-color: transparent !important;
    }}
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {config.COLOR_PANEL};
        border-right: 1px solid {config.COLOR_BORDER};
    }}
    /* Panels / Cards */
    .stMarkdown, .stSelectbox, .stTextInput, .stNumberInput {{
        color: {config.COLOR_TEXT} !important;
    }}
    /* Monospace for specific elements */
    code, pre, .stMetric, .stDataFrame {{
        font-family: 'JetBrains Mono', 'IBM Plex Mono', monospace !important;
    }}
    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: {config.COLOR_TEXT} !important;
        font-family: 'JetBrains Mono', monospace !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    /* Buttons */
    .stButton > button {{
        background-color: {config.COLOR_PANEL_ELEVATED};
        color: {config.COLOR_PRIMARY};
        border: 1px solid {config.COLOR_BORDER};
        font-family: 'JetBrains Mono', monospace;
        text-transform: uppercase;
        transition: all 0.2s ease-in-out;
        border-radius: 2px;
    }}
    .stButton > button:hover {{
        background-color: {config.COLOR_PRIMARY};
        color: {config.COLOR_BG};
        border-color: {config.COLOR_PRIMARY};
        box-shadow: 0 0 10px {config.COLOR_PRIMARY}40;
    }}
    .stButton > button[data-baseweb="button"] p {{
        color: inherit;
    }}
    /* Primary Button */
    .stButton > button[kind="primary"] {{
        background-color: {config.COLOR_PRIMARY}20;
        border-color: {config.COLOR_PRIMARY};
        color: {config.COLOR_PRIMARY};
    }}
    /* Inputs */
    .stTextInput > div > div > input, .stNumberInput > div > div > input {{
        background-color: {config.COLOR_PANEL_ELEVATED};
        color: {config.COLOR_TEXT};
        border: 1px solid {config.COLOR_BORDER};
        border-radius: 2px;
        font-family: 'JetBrains Mono', monospace;
    }}
    .stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus {{
        border-color: {config.COLOR_SECONDARY};
        box-shadow: 0 0 5px {config.COLOR_SECONDARY}40;
    }}
    /* Chat bubbles */
    [data-testid="stChatMessage"] {{
        background-color: {config.COLOR_PANEL};
        border: 1px solid {config.COLOR_BORDER};
        border-radius: 4px;
        margin-bottom: 1rem;
    }}
    [data-testid="stChatMessage"][data-testid="stChatMessage-user"] {{
        background-color: {config.COLOR_PANEL_ELEVATED};
        border-color: {config.COLOR_SECONDARY}40;
        border-left: 3px solid {config.COLOR_SECONDARY};
    }}
    [data-testid="stChatMessage"][data-testid="stChatMessage-assistant"] {{
        border-color: {config.COLOR_PRIMARY}40;
        border-left: 3px solid {config.COLOR_PRIMARY};
    }}
    /* Metrics */
    [data-testid="stMetricValue"] {{
        color: {config.COLOR_PRIMARY};
        font-weight: bold;
    }}
    [data-testid="stMetricLabel"] {{
        color: {config.COLOR_MUTED};
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
    }}
    /* Dividers */
    hr {{
        border-top: 1px solid {config.COLOR_BORDER};
    }}
    /* Alerts/Warnings */
    .stAlert {{
        background-color: {config.COLOR_PANEL_ELEVATED};
        border-radius: 2px;
    }}
    [data-testid="stAlert"] [data-testid="markdownContainer"] p {{
        font-family: 'JetBrains Mono', monospace;
    }}
    /* Expanders */
    .streamlit-expanderHeader {{
        font-family: 'JetBrains Mono', monospace;
        background-color: {config.COLOR_PANEL_ELEVATED};
        color: {config.COLOR_TEXT};
        border: 1px solid {config.COLOR_BORDER};
    }}
    .streamlit-expanderContent {{
        border-left: 1px solid {config.COLOR_BORDER};
        border-right: 1px solid {config.COLOR_BORDER};
        border-bottom: 1px solid {config.COLOR_BORDER};
    }}
    /* Subtle scanlines effect overlay on main app */
    .stApp::before {{
        content: " ";
        display: block;
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
        z-index: 2;
        background-size: 100% 2px, 3px 100%;
        pointer-events: none;
        opacity: 0.15;
    }}
    
    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: {config.COLOR_BG};
    }}
    ::-webkit-scrollbar-thumb {{
        background: {config.COLOR_BORDER};
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {config.COLOR_MUTED};
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
