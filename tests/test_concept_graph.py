import pytest
from unittest.mock import MagicMock
from modules.concept_graph import extract_concept_edges
from modules.db import Concept

def test_extract_concept_edges_too_few_concepts():
    # Arrange
    mock_db = MagicMock()

    # Case 1: 0 concepts
    mock_db.query.return_value.filter_by.return_value.all.return_value = []

    result = extract_concept_edges(course_id=1, context="some context", db=mock_db, api_key="fake")
    assert result == 0

    # Case 2: 1 concept
    mock_db.query.return_value.filter_by.return_value.all.return_value = [Concept(id=1, course_id=1, label="concept1")]

    result = extract_concept_edges(course_id=1, context="some context", db=mock_db, api_key="fake")
    assert result == 0
