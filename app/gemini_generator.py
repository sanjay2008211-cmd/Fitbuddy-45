from app.gemini_client import gemini_service


def generate_workout_gemini(
    username: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
    experience: str = "beginner",
) -> str:
    return gemini_service.workout_plan(
        username, age, weight, goal, intensity, experience
    )
