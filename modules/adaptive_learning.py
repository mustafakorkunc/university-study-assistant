from datetime import datetime, timedelta
import math
from sqlalchemy.orm import Session
from modules.db import Concept, Flashcard, QuestionAttempt, Misconception, FlashcardReviewEvent

class LearningPolicy:
    WEIGHT_PERFECT_FLASHCARD = 1.0
    WEIGHT_FAILED_FLASHCARD = -1.5
    WEIGHT_CORRECT_EXAM = 1.5
    WEIGHT_INCORRECT_EXAM = -1.0
    WEIGHT_MISCONCEPTION_ACTIVE = -2.0
    WEIGHT_MISCONCEPTION_RESOLVED = 0.5
    DECAY_RATE_PER_DAY = 0.05

def calculate_forgetting_risk(last_seen_date, confidence, interval):
    if not last_seen_date:
        return 1.0
    days_elapsed = (datetime.utcnow() - last_seen_date).days
    if interval <= 0: interval = 1.0
    retention = math.exp(-days_elapsed / interval)
    base_risk = 1.0 - retention
    risk = base_risk * (1.1 - confidence)
    return min(max(risk, 0.0), 1.0)

def get_concept_state(user_id: int, course_id: int, concept_id: int, db: Session):
    concept = db.query(Concept).filter_by(id=concept_id, course_id=course_id).first()
    if not concept:
        return None
        
    attempts = db.query(QuestionAttempt).filter_by(concept_id=concept.id).all()
    misconceptions = db.query(Misconception).filter_by(concept_id=concept.id).all()
    reviews = db.query(FlashcardReviewEvent).join(Flashcard).filter(Flashcard.concept_id == concept.id).all()
    
    correct_count = sum(1 for a in attempts if a.score >= 80)
    incorrect_count = sum(1 for a in attempts if a.score < 80)
    evidence_count = len(attempts) + len(reviews)
    
    raw_score = 0.0
    for a in attempts: raw_score += LearningPolicy.WEIGHT_CORRECT_EXAM if a.score >= 80 else LearningPolicy.WEIGHT_INCORRECT_EXAM
    for r in reviews: raw_score += LearningPolicy.WEIGHT_PERFECT_FLASHCARD if r.quality >= 4 else LearningPolicy.WEIGHT_FAILED_FLASHCARD
    for m in misconceptions: raw_score += LearningPolicy.WEIGHT_MISCONCEPTION_ACTIVE if m.status == "active" else LearningPolicy.WEIGHT_MISCONCEPTION_RESOLVED
        
    mastery = 1 / (1 + math.exp(-0.5 * raw_score))
    
    avg_confidence = sum(r.quality / 5.0 for r in reviews) / len(reviews) if reviews else 0.5
    
    cards = db.query(Flashcard).filter_by(concept_id=concept.id).all()
    max_interval = max([c.interval for c in cards] + [1])
    
    forgetting_risk = calculate_forgetting_risk(concept.last_seen, avg_confidence, max_interval)
    
    # Save to db
    concept.mastery_score = mastery
    concept.confidence = avg_confidence
    db.commit()
    
    return {
        "concept_id": concept.id,
        "label": concept.label,
        "mastery_score": mastery,
        "confidence_score": avg_confidence,
        "evidence_count": evidence_count,
        "correct_count": correct_count,
        "incorrect_count": incorrect_count,
        "forgetting_risk": forgetting_risk,
        "last_seen": concept.last_seen
    }

def get_course_learning_state(user_id: int, course_id: int, db: Session):
    concepts = db.query(Concept).filter_by(course_id=course_id).all()
    states = [get_concept_state(user_id, course_id, c.id, db) for c in concepts]
    
    if not states:
        return {"status": "No Data", "score": 0, "breakdown": {}}
        
    avg_mastery = sum(s["mastery_score"] for s in states) / len(states)
    active_misconceptions = db.query(Misconception).filter_by(course_id=course_id, status="active").count()
    
    readiness = avg_mastery * 100 - (active_misconceptions * 10)
    readiness = max(0, min(readiness, 100))
    status = "Ready" if readiness >= 80 else "Needs Study"
    
    return {
        "status": status,
        "score": int(readiness),
        "breakdown": {
            "Concept Mastery": f"{int(avg_mastery * 100)}%",
            "Active Misconceptions": str(active_misconceptions)
        }
    }

def get_next_best_action(user_id: int, course_id: int, db: Session):
    now = datetime.utcnow()
    
    due_cards = db.query(Flashcard).filter(Flashcard.course_id == course_id, Flashcard.next_review <= now).count()
    if due_cards > 10:
        return {
            "action": "REVIEW",
            "concept": None,
            "title": f"Review {due_cards} due cards",
            "reason": "Spaced repetition is critical.",
            "estimated_effort": "15 mins"
        }
        
    active_misconception = db.query(Misconception).filter_by(course_id=course_id, status="active").first()
    if active_misconception:
        concept = db.query(Concept).get(active_misconception.concept_id) if active_misconception.concept_id else None
        concept_label = concept.label if concept else "General"
        return {
            "action": "FIX_MISCONCEPTION",
            "concept": concept_label,
            "title": f"Fix a recurring misconception",
            "reason": f"You have an unresolved misconception: '{active_misconception.category}'.",
            "estimated_effort": "10 mins"
        }
        
    concepts = db.query(Concept).filter_by(course_id=course_id).all()
    if concepts:
        states = [get_concept_state(user_id, course_id, c.id, db) for c in concepts]
        states.sort(key=lambda x: x["mastery_score"])
        weakest = states[0]
        
        if weakest["mastery_score"] < 0.6:
            return {
                "action": "PRACTICE",
                "concept": weakest["label"],
                "title": f"Practice {weakest['label']}",
                "reason": f"Your mastery is low ({int(weakest['mastery_score']*100)}%).",
                "estimated_effort": "10 mins"
            }
            
        states.sort(key=lambda x: x["forgetting_risk"], reverse=True)
        riskiest = states[0]
        if riskiest["forgetting_risk"] > 0.7:
            return {
                "action": "TAKE_MINI_EXAM",
                "concept": riskiest["label"],
                "title": f"Test your understanding of {riskiest['label']}",
                "reason": "You haven't seen this in a while.",
                "estimated_effort": "20 mins"
            }
            
    if due_cards > 0:
        return {
            "action": "REVIEW",
            "concept": None,
            "title": f"Review {due_cards} due cards",
            "reason": "Clear remaining reviews.",
            "estimated_effort": "5 mins"
        }
        
    return {
        "action": "LEARN_NEW",
        "concept": None,
        "title": "Learn something new",
        "reason": "You're all caught up!",
        "estimated_effort": "Open"
    }

def get_recurring_misconceptions(user_id: int, course_id: int, db: Session):
    # Only pull misconceptions from this course
    active = db.query(Misconception).filter_by(course_id=course_id, status="active").all()

    # Batch fetch concepts to avoid N+1 query problem
    concept_ids = [m.concept_id for m in active if m.concept_id]
    concepts_map = {}
    if concept_ids:
        concepts = db.query(Concept).filter(Concept.id.in_(concept_ids)).all()
        concepts_map = {c.id: c for c in concepts}

    recurring = []
    for m in active:
        concept = concepts_map.get(m.concept_id) if m.concept_id else None
        recurring.append({
            "concept": concept.label if concept else "General",
            "category": m.category,
            "description": m.description
        })
    return recurring
