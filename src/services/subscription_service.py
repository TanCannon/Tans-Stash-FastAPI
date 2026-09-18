from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from src.models.user_model import Subscription

def create_subscription(user_id: str, plan_id: str, db: Session):
    #step1: deactivate old subscription
    db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == "active"
        ).update({"status":"expired"})

    #step2: add new subscription
    new_sub = Subscription(
        user_id = user_id,
        plan_id = plan_id,
        status = "active",
        start_date = datetime.now(),
        end_date = datetime.now() + timedelta(days=30) #30 days say, need to add this field in plan model
    )

    db.add(new_sub)
    db.commit()