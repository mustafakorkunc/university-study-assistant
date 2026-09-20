from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import json
import config
from modules.db import Concept, ConceptEdge

class EdgeOutput(BaseModel):
    source_concept_label: str
    target_concept_label: str
    relationship_type: str = Field(description="Must be one of: PREREQUISITE, RELATED_TO, PART_OF, CAUSES, CONTRASTS_WITH, EXAMPLE_OF")
    evidence: str = Field(description="A brief explanation of why this relationship exists.")

class GraphOutput(BaseModel):
    edges: list[EdgeOutput]

def extract_concept_edges(course_id, context, db, api_key):
    """
    Extracts relationships between existing concepts based on the provided context.
    """
    concepts = db.query(Concept).filter_by(course_id=course_id).all()
    if len(concepts) < 2:
        return 0
        
    concept_labels = [c.label for c in concepts]
    
    prompt = (
        f"You are a knowledge architect. Given the following text context, identify relationships between these known concepts: {', '.join(concept_labels)}.\n"
        "Return a JSON array of edges linking the concepts.\n\n"
        f"Context:\n{context}"
    )
    
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model=config.LLM_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GraphOutput,
                temperature=0.1
            )
        )
        data = GraphOutput.model_validate_json(response.text)
        
        edges_added = 0
        for edge in data.edges:
            # Resolve concepts
            source = next((c for c in concepts if c.label.lower() == edge.source_concept_label.lower()), None)
            target = next((c for c in concepts if c.label.lower() == edge.target_concept_label.lower()), None)
            
            if source and target and source.id != target.id:
                # Check if exists
                existing = db.query(ConceptEdge).filter_by(
                    source_concept_id=source.id,
                    target_concept_id=target.id
                ).first()
                
                if not existing:
                    db_edge = ConceptEdge(
                        source_concept_id=source.id,
                        target_concept_id=target.id,
                        relationship_type=edge.relationship_type,
                        evidence=edge.evidence
                    )
                    db.add(db_edge)
                    edges_added += 1
        db.commit()
        return edges_added
    except Exception as e:
        print(f"Error extracting edges: {e}")
        return 0
