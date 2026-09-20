import pytest
from unittest.mock import MagicMock, patch
from modules.document_processor import process_file

def test_process_file_none():
    assert process_file(None) == ""

def test_process_file_txt_success():
    mock_file = MagicMock()
    mock_file.name = "test.txt"
    mock_file.getvalue.return_value = b"Hello, World!"

    assert process_file(mock_file) == "Hello, World!"

def test_process_file_txt_error():
    mock_file = MagicMock()
    mock_file.name = "test.txt"
    mock_file.getvalue.side_effect = Exception("Mock error")

    assert process_file(mock_file) == "Error reading TXT: Mock error"

def test_process_file_unsupported():
    mock_file = MagicMock()
    mock_file.name = "test.jpg"

    assert process_file(mock_file) == "Unsupported file format. Please upload a PDF or TXT file."

@patch("modules.document_processor.PdfReader")
def test_process_file_pdf_success(mock_pdf_reader_class):
    mock_file = MagicMock()
    mock_file.name = "test.pdf"

    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = "Page 1 content"
    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = "Page 2 content"

    mock_pdf_reader_instance = MagicMock()
    mock_pdf_reader_instance.pages = [mock_page1, mock_page2]
    mock_pdf_reader_class.return_value = mock_pdf_reader_instance

    assert process_file(mock_file) == "Page 1 content\nPage 2 content"

@patch("modules.document_processor.PdfReader")
def test_process_file_pdf_error(mock_pdf_reader_class):
    mock_file = MagicMock()
    mock_file.name = "test.pdf"

    mock_pdf_reader_class.side_effect = Exception("Mock PDF error")

    assert process_file(mock_file) == "Error reading PDF: Mock PDF error"
