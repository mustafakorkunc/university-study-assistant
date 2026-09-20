class GroundingState:
    GROUNDED = "GROUNDED"
    PARTIALLY_GROUNDED = "PARTIALLY_GROUNDED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

def evaluate_grounding(evidence, min_chunks=1):
    """
    Evaluates whether the retrieved evidence is sufficient to ground a response.
    Returns (GroundingState, msg)
    
    Heuristic:
    - result count: Need at least 1 result.
    - top score: Top RRF score must be > 0.012 for GROUNDED.
    - score margin: If top score is close to the second, it shows diversity. If only one weak chunk matches, PARTIALLY_GROUNDED.
    - (Assumes RRF implicitly combines lexical and semantic relevance).
    """
    if not evidence or len(evidence) < min_chunks:
        return GroundingState.INSUFFICIENT_EVIDENCE, "I couldn't find enough evidence in your course materials."
        
    top_score = evidence[0].get("relevance_score", 0.0)
    second_score = evidence[1].get("relevance_score", 0.0) if len(evidence) > 1 else 0.0
    
    if top_score < 0.008:
        return GroundingState.INSUFFICIENT_EVIDENCE, "I found some documents, but they do not seem relevant enough to answer definitively."
        
    if top_score < 0.015:
        # Check margin
        if len(evidence) == 1 or (top_score - second_score) > 0.005:
            # Only one weak piece of evidence stands out
            return GroundingState.PARTIALLY_GROUNDED, "I found some related information, but the evidence is weak. Take this with caution."
            
    return GroundingState.GROUNDED, ""

def validate_citation(chunk_id, course_id, retrieved_evidence, db):
    """
    Validates a structured citation returned by the AI.
    1. Checks if chunk_id was actually in the retrieved evidence payload.
    2. Checks if chunk belongs to the correct course.
    """
    # Verify it was in the AI's prompt evidence
    in_evidence = any(e["chunk_id"] == chunk_id for e in retrieved_evidence)
    if not in_evidence:
        return False, "Citation invented: Not in provided evidence."
        
    from modules.db import Chunk, Document
    # Verify DB provenance strictly
    chunk = db.query(Chunk).join(Document).filter(
        Chunk.id == chunk_id,
        Document.course_id == course_id
    ).first()
    
    if not chunk:
        return False, "Citation invalid: Does not exist in this course."
        
    return True, "Valid"
