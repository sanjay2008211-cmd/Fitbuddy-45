from app.gemini_client import gemini_service


def generate_nutrition_tip_with_flash(goal: str, weight: float) -> str:
    return gemini_service.nutrition_tip(goal, weight)
