import secrets
import hashlib
from sqlalchemy.orm import Session

from src.models.user_model import User, APIKey, Subscription, PlanProduct
from src.models.tool_model import Tool

API_KEY_PREFIX = "ts_live_"

def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()

def create_api_key(user_id: str, db: Session):
    """
    Generate an API key and store only its hash.
    Returns the raw key ONLY once.
    """

    # Validate user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User does not exist")

    # Generate key
    raw_key = secrets.token_urlsafe(32)
    full_key = f"{API_KEY_PREFIX}{raw_key}"

    hashed_key = hash_key(full_key)

    api_key = APIKey(
        user_id=user_id,
        key_hash=hashed_key,
        is_active=True
    )

    try:
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
    except Exception:
        db.rollback()
        raise

    return full_key

def validate_api_key(db, incoming_key: str):
    hashed = hash_key(incoming_key)

    key = db.query(APIKey).filter(
        APIKey.key_hash == hashed
    ).first()

    if not key:
        return None

    if not key.is_active:
        return None

    return {
        "user_id": key.user_id,
        "api_key_id": key.id
    }

def has_access_to_tool(db, user_id: str, tool_id: str):
    if (user_id == '' or tool_id == ''):
        return False
    
    return db.query(PlanProduct).join(
        Subscription, Subscription.plan_id == PlanProduct.plan_id
    ).filter(
        Subscription.user_id == user_id,
        Subscription.status == "active",
        PlanProduct.tool_id == tool_id
    ).first() is not None


