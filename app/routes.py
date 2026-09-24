from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.crud import (
    delete_user,
    get_all_plans,
    get_all_users,
    get_latest_plan,
    get_user,
    save_plan,
    save_user,
    update_plan,
)
from app.database import get_db
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.gemini_generator import generate_workout_gemini
from app.schemas import FeedbackRequest, UserInput
from app.updated_plan import update_workout_plan

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    user_id: str = Form(...),
    username: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    experience: str = Form("beginner"),
    db: Session = Depends(get_db),
):
    try:
        data = UserInput(
            user_id=user_id,
            username=username,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity.lower(),
            experience=experience.lower(),
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": str(exc)},
            status_code=422,
        )

    save_user(db, data)

    workout_plan = generate_workout_gemini(
        data.username,
        data.age,
        data.weight,
        data.goal,
        data.intensity,
        data.experience,
    )
    nutrition_tip = generate_nutrition_tip_with_flash(data.goal, data.weight)
    save_plan(db, data.user_id, workout_plan, nutrition_tip)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "user": data.model_dump(),
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip,
            "updated": False,
            "message": None,
        },
    )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    data = FeedbackRequest(user_id=user_id, feedback=feedback)
    user = get_user(db, data.user_id)
    plan = get_latest_plan(db, data.user_id)

    if not user or not plan:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": "User ID not found. Generate a plan first."},
            status_code=404,
        )

    revised = update_workout_plan(
        plan.original_plan,
        data.feedback,
        user.goal,
        user.intensity,
    )
    update_plan(db, data.user_id, revised, data.feedback)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "age": user.age,
                "weight": user.weight,
                "goal": user.goal,
                "intensity": user.intensity,
                "experience": user.experience,
            },
            "workout_plan": revised,
            "nutrition_tip": plan.nutrition_tip,
            "updated": True,
            "message": "Your workout plan has been updated using your feedback.",
        },
    )


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, db: Session = Depends(get_db)):
    users = get_all_users(db)
    plans = get_all_plans(db)
    plan_by_user = {}
    for plan in plans:
        plan_by_user.setdefault(plan.user_id, plan)

    rows = [{"user": u, "plan": plan_by_user.get(u.user_id)} for u in users]
    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"rows": rows},
    )


@router.post("/delete-user/{user_id}")
def remove_user(user_id: str, db: Session = Depends(get_db)):
    delete_user(db, user_id)
    return RedirectResponse(url="/view-all-users", status_code=303)


# JSON APIs for testing/integration
@router.post("/api/generate-workout")
def api_generate_workout(data: UserInput, db: Session = Depends(get_db)):
    save_user(db, data)
    workout = generate_workout_gemini(
        data.username, data.age, data.weight,
        data.goal, data.intensity, data.experience
    )
    tip = generate_nutrition_tip_with_flash(data.goal, data.weight)
    save_plan(db, data.user_id, workout, tip)
    return JSONResponse({
        "user_id": data.user_id,
        "workout_plan": workout,
        "nutrition_tip": tip,
    })


@router.post("/api/submit-feedback")
def api_submit_feedback(data: FeedbackRequest, db: Session = Depends(get_db)):
    user = get_user(db, data.user_id)
    plan = get_latest_plan(db, data.user_id)
    if not user or not plan:
        return JSONResponse({"detail": "User ID not found."}, status_code=404)

    revised = update_workout_plan(
        plan.original_plan, data.feedback, user.goal, user.intensity
    )
    update_plan(db, data.user_id, revised, data.feedback)
    return {"user_id": data.user_id, "updated_plan": revised}


@router.get("/api/users")
def api_users(db: Session = Depends(get_db)):
    users = get_all_users(db)
    return [
        {
            "user_id": u.user_id,
            "username": u.username,
            "age": u.age,
            "weight": u.weight,
            "goal": u.goal,
            "intensity": u.intensity,
            "experience": u.experience,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]


@router.get("/health")
def health():
    from app.gemini_client import gemini_service
    return {"status": "ok", "gemini_configured": gemini_service.live}
