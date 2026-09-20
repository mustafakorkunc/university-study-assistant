from pypdf import PdfReader
import io

def process_file(uploaded_file):
    """
    Reads an uploaded file (PDF or TXT) and extracts text.
    """
    if uploaded_file is None:
        return ""
    
    filename = uploaded_file.name.lower()
    text = ""
    
    if filename.endswith(".pdf"):
        try:
            pdf_reader = PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            text = f"Error reading PDF: {e}"
    elif filename.endswith(".txt"):
        try:
            text = uploaded_file.getvalue().decode("utf-8")
        except Exception as e:
            text = f"Error reading TXT: {e}"
    else:
        text = "Unsupported file format. Please upload a PDF or TXT file."
        
    return text.strip()
