import json
import os
from typing import Any

try:
    from google import genai
    from google.genai import types
except ImportError:  # pragma: no cover
    genai = None
    types = None


class GeminiService:
    """Gemini integration with a safe local fallback for development/testing."""

    def __init__(self) -> None:
        self.api_key = os.getenv("GOOGLE_API_KEY", "").strip()
        self.workout_model = os.getenv("GEMINI_WORKOUT_MODEL", "gemini-2.5-flash")
        self.tip_model = os.getenv("GEMINI_TIP_MODEL", "gemini-2.5-flash")
        self.client = None
        if self.api_key and genai:
            self.client = genai.Client(api_key=self.api_key)

    @property
    def live(self) -> bool:
        return self.client is not None

    def generate(self, prompt: str, model: str) -> str:
        if not self.client:
            return ""
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.6,
                max_output_tokens=5000,
            ),
        )
        return (response.text or "").strip()

    def workout_plan(
        self,
        username: str,
        age: int,
        weight: float,
        goal: str,
        intensity: str,
        experience: str,
    ) -> str:
        prompt = f"""
You are FitBuddy, a fitness-planning assistant.

Create a safe, practical 7-day workout plan for:
Name: {username}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Intensity: {intensity}
Experience: {experience}

Requirements:
- Give exactly 7 days.
- Each day must contain: Focus, Warm-up (5-10 min), Main workout
  with exercises and sets/reps or duration, Rest, Cool-down/recovery.
- Include appropriate rest/recovery.
- Adapt difficulty to the stated experience and intensity.
- Avoid diagnosing or treating medical conditions.
- Add a short safety note telling the user to stop if they feel pain
  and consult a qualified professional when appropriate.
- Keep the plan easy to read. Do not use markdown tables.
"""
        result = self.generate(prompt, self.workout_model)
        return result or self._fallback_plan(goal, intensity, experience)

    def nutrition_tip(self, goal: str, weight: float) -> str:
        prompt = f"""
Give one concise, practical nutrition or recovery tip for a fitness user.
Goal: {goal}
Weight: {weight} kg
Avoid prescribing medical diets. Mention hydration and balanced food where useful.
Keep the answer under 120 words.
"""
        result = self.generate(prompt, self.tip_model)
        return result or (
            f"For {goal}, focus on balanced meals with adequate protein, vegetables, "
            "whole-food carbohydrates and healthy fats. Stay hydrated and prioritize "
            "consistent sleep and recovery. Individual nutrition needs vary, so consult "
            "a qualified dietitian for personalized advice."
        )

    def update_plan(self, original_plan: str, feedback: str, goal: str, intensity: str) -> str:
        prompt = f"""
You are updating a 7-day fitness plan.

Original plan:
{original_plan}

User feedback:
{feedback}

Goal: {goal}
Preferred intensity: {intensity}

Return a complete revised 7-day plan, not just a list of changes.
Preserve useful parts of the original plan while applying the feedback.
Keep the same safety requirements and include warm-up, workout, rest and cooldown.
Do not provide medical diagnosis or treatment.
"""
        result = self.generate(prompt, self.workout_model)
        return result or self._fallback_update(original_plan, feedback)

    @staticmethod
    def _fallback_plan(goal: str, intensity: str, experience: str) -> str:
        days = [
            ("Day 1", "Full body strength"),
            ("Day 2", "Cardio + mobility"),
            ("Day 3", "Upper body"),
            ("Day 4", "Active recovery"),
            ("Day 5", "Lower body"),
            ("Day 6", "Core + light cardio"),
            ("Day 7", "Rest and recovery"),
        ]
        lines = [
            f"FITBUDDY 7-DAY PLAN — Goal: {goal} | Intensity: {intensity} | Level: {experience}",
            ""
        ]
        for day, focus in days:
            lines += [
                day,
                f"Focus: {focus}",
                "Warm-up: 5-10 minutes of easy movement and dynamic mobility.",
                "Main workout: Choose 3-5 suitable exercises. Perform 2-3 sets of 8-15 reps "
                "or 20-40 seconds per exercise, using controlled form.",
                "Rest: 45-90 seconds between sets; take longer if needed.",
                "Cool-down: 5-10 minutes of easy walking and gentle stretching.",
                "",
            ]
        lines.append("Safety: Stop if you experience pain, dizziness or unusual symptoms and seek professional advice when appropriate.")
        return "\n".join(lines)

    @staticmethod
    def _fallback_update(original: str, feedback: str) -> str:
        return (
            original
            + "\n\nUPDATED USING FEEDBACK\n"
            + f"User feedback applied: {feedback}\n"
            + "Adjust exercise volume or rest periods gradually and prioritize proper form."
        )


gemini_service = GeminiService()
