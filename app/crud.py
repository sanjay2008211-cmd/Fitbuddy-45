from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Plan, User


def save_user(db: Session, data) -> User:
    user = db.scalar(select(User).where(User.user_id == data.user_id))
    if user:
        user.username = data.username
        user.age = data.age
        user.weight = data.weight
        user.goal = data.goal
        user.intensity = data.intensity
        user.experience = data.experience
    else:
        user = User(**data.model_dump())
        db.add(user)
    db.commit()
    db.refresh(user)
    return user


def save_plan(db: Session, user_id: str, original_plan: str, nutrition_tip: str) -> Plan:
    plan = Plan(
        user_id=user_id,
        original_plan=original_plan,
        nutrition_tip=nutrition_tip,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_user(db: Session, user_id: str) -> User | None:
    return db.scalar(select(User).where(User.user_id == user_id))


def get_latest_plan(db: Session, user_id: str) -> Plan | None:
    return db.scalar(
        select(Plan)
        .where(Plan.user_id == user_id)
        .order_by(Plan.created_at.desc())
    )


def get_original_plan(db: Session, user_id: str) -> str | None:
    plan = get_latest_plan(db, user_id)
    return plan.original_plan if plan else None


def update_plan(db: Session, user_id: str, updated_plan: str, feedback: str) -> Plan | None:
    plan = get_latest_plan(db, user_id)
    if not plan:
        return None
    plan.updated_plan = updated_plan
    plan.last_feedback = feedback
    plan.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(plan)
    return plan


def get_all_users(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.created_at.desc())).all())


def get_all_plans(db: Session) -> list[Plan]:
    return list(db.scalars(select(Plan).order_by(Plan.created_at.desc())).all())


def delete_user(db: Session, user_id: str) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False
    plans = list(db.scalars(select(Plan).where(Plan.user_id == user_id)).all())
    for plan in plans:
        db.delete(plan)
    db.delete(user)
    db.commit()
    return True
