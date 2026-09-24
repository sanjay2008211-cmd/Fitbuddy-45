from app.gemini_client import gemini_service


def update_workout_plan(
    original_plan: str,
    feedback: str,
    goal: str,
    intensity: str,
) -> str:
    return gemini_service.update_plan(original_plan, feedback, goal, intensity)
