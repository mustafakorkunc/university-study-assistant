from modules.adaptive_learning import get_next_best_action

def generate_study_session_plan(user_id, course_id, db):
    """
    Creates a dynamic queue of study tasks based on the Next Best Action engine.
    """
    # For now, we will simulate the dynamic session by pulling the top 3 best actions.
    # A true implementation would iterate state virtually.
    
    plan = []
    
    # 1. Primary Action
    action1 = get_next_best_action(user_id, course_id, db)
    plan.append(action1)
    
    # In a full implementation, we would then query the second best action.
    # Here we return the primary action to feed the UI task executor.
    
    return plan

def summarize_session(completed_tasks):
    """
    Generates a genuine session summary from a list of completed task dicts.
    """
    if not completed_tasks:
        return "No tasks completed."
        
    summary = f"Completed {len(completed_tasks)} tasks.\n"
    for t in completed_tasks:
        summary += f"- {t['action']}: {t.get('concept', 'General')}\n"
        
    return summary
