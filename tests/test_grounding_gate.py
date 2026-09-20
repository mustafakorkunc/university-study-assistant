import pytest
from modules.grounding import evaluate_grounding, GroundingState

def test_grounding_gate():
    # 1. No evidence
    state, msg = evaluate_grounding([])
    assert state == GroundingState.INSUFFICIENT_EVIDENCE
    
    # 2. Strong evidence
    evidence = [{"text": "A", "relevance_score": 0.05}]
    state, msg = evaluate_grounding(evidence)
    assert state == GroundingState.GROUNDED
    
    # 3. Weak evidence
    evidence = [{"text": "A", "relevance_score": 0.005}]
    state, msg = evaluate_grounding(evidence)
    assert state == GroundingState.INSUFFICIENT_EVIDENCE
    
    # 4. Partial evidence
    evidence = [{"text": "A", "relevance_score": 0.012}]
    state, msg = evaluate_grounding(evidence)
    assert state == GroundingState.PARTIALLY_GROUNDED
