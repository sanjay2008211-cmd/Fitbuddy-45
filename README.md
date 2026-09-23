# FitBuddy – AI Fitness Plan Generator

FitBuddy is a FastAPI + Jinja2 + SQLite web application based on the supplied project documentation.

## Features

- User profile: name, user ID, age, weight, goal, intensity and experience
- AI-generated 7-day workout plan
- AI nutrition/recovery tip
- Feedback-based plan regeneration
- SQLite persistence with SQLAlchemy
- Admin/coach dashboard
- JSON API endpoints and FastAPI Swagger docs
- Safe local fallback when `GOOGLE_API_KEY` is not configured

## Architecture

```text
Browser
  |
  v
FastAPI routes.py
  |------> Jinja2 templates
  |------> SQLAlchemy -> SQLite
  |
  +------> GeminiService
              |---- workout model
              +---- nutrition model
```

The supplied documentation specifies Gemini Pro for workout generation/update and Gemini Flash for nutrition tips. The code keeps those roles separate while making the exact model names configurable through environment variables.

## Windows setup

```powershell
py -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and add your Gemini API key.

## Run

```powershell
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/view-all-users
- http://127.0.0.1:8000/health

## Test without an API key

The app has a deterministic fallback so the UI and database can be tested without Gemini. Do not treat fallback output as AI-generated output.

## API examples

### Generate

POST `/api/generate-workout`

```json
{
  "user_id": "FB001",
  "username": "Alex",
  "age": 21,
  "weight": 65,
  "goal": "muscle gain",
  "intensity": "medium",
  "experience": "beginner"
}
```

### Feedback

POST `/api/submit-feedback`

```json
{
  "user_id": "FB001",
  "feedback": "Add more cardio and keep Day 4 as a full rest day."
}
```

## Project tree

```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── gemini_client.py
│   ├── gemini_generator.py
│   ├── gemini_flash_generator.py
│   └── updated_plan.py
├── templates/
│   ├── index.html
│   ├── result.html
│   └── all_users.html
├── static/
│   └── css/
│       └── style.css
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Notes

This is a wellness application, not a medical diagnostic or treatment system. The AI prompt instructs the model to avoid medical diagnosis/treatment and to include safety guidance.
