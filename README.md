# University Study Assistant

A comprehensive, AI-powered web application designed to help university students study more effectively. Built with Python, Streamlit, and the Google Gemini API.

## Features

1. **Document Processing**: Upload your course notes (PDF/TXT) and automatically extract text.
2. **Socratic Tutor**: An interactive chat interface that guides you to answers using Socratic questioning, referencing your uploaded notes.
3. **Quiz & Flashcards**: Automatically generate multiple-choice quizzes from your study material, complete with immediate feedback and explanations.
4. **Smart Summary**: Generate structured cheat-sheets, key terms, and core concepts from your documents.

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- A Google Gemini API key

### Installation

1. Clone this repository or download the source code.
2. Navigate to the project directory:
   ```bash
   cd university_study_assistant
   ```
3. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create a `.env` file in the root directory (you can copy `.env.example`):
   ```bash
   cp .env.example .env
   ```
6. Add your Gemini API key to the `.env` file:
   ```env
   GEMINI_API_KEY="your_api_key_here"
   ```

### Running the Application

Start the Streamlit server:
```bash
streamlit run app.py
```

The application will open in your default web browser.

## Project Structure
- `app.py`: Main Streamlit application and UI layout.
- `config.py`: Environment configuration and model settings.
- `modules/`: Contains core logic for document processing, Socratic tutoring, quiz generation, and summarization.
