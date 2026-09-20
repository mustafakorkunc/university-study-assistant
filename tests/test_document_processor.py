import io
import pytest
from modules.document_processor import process_file

def test_process_file_pdf_error_handling():
    """Test that a malformed PDF file triggers the exception block."""
    mock_file = io.BytesIO(b"This is definitely not a valid PDF file stream")
    mock_file.name = "malformed_test.pdf"

    result = process_file(mock_file)

    assert result.startswith("Error reading PDF:")

def test_process_file_txt_happy_path():
    """Test that a valid txt file is read correctly."""
    mock_file = io.BytesIO(b"Hello world")
    mock_file.name = "hello.txt"

    result = process_file(mock_file)

    assert result == "Hello world"

def test_process_file_unsupported_format():
    """Test that an unsupported file format returns the appropriate message."""
    mock_file = io.BytesIO(b"image data")
    mock_file.name = "image.png"

    result = process_file(mock_file)

    assert result == "Unsupported file format. Please upload a PDF or TXT file."

def test_process_file_none():
    """Test that a None file returns empty string."""
    result = process_file(None)
    assert result == ""
