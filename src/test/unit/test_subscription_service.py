from utils_for_unit_test import *

from datetime import datetime, timedelta

from src.models import Subscription
from src.services.subscription_service import create_subscription

def test_create_subscription_replaces_old_one(db):
    user_id = "user_123"
    plan_id_old = "basic"
    plan_id_new = "pro"

    # Step 1: Create an existing active subscription
    old_sub = Subscription(
        user_id=user_id,
        plan_id=plan_id_old,
        status="active",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30)
    )

    db.add(old_sub)
    db.commit()

    # Step 2: Call function
    create_subscription(user_id, plan_id_new, db)

    # Step 3: Fetch all subscriptions for user
    subs = db.query(Subscription).filter(
        Subscription.user_id == user_id
    ).all()

    # Step 4: Assertions

    # There should be 2 subscriptions total
    assert len(subs) == 2

    # Only ONE active subscription
    active_subs = [s for s in subs if s.status == "active"]
    assert len(active_subs) == 1

    # Old one should be expired
    expired_subs = [s for s in subs if s.status == "expired"]
    assert len(expired_subs) == 1

    # New one should have correct plan
    assert active_subs[0].plan_id == plan_id_new