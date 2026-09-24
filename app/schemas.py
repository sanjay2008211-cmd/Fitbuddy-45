from typing import Literal

from pydantic import BaseModel, Field, field_validator


class UserInput(BaseModel):
    user_id: str = Field(min_length=2, max_length=80)
    username: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=20, lt=400)
    goal: str = Field(min_length=2, max_length=100)
    intensity: Literal["low", "medium", "high"]
    experience: Literal["beginner", "intermediate", "advanced"] = "beginner"

    @field_validator("user_id", "username", "goal")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        return value


class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=2, max_length=80)
    feedback: str = Field(min_length=3, max_length=2000)
