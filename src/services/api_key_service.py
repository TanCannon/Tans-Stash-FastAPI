import secrets
import hashlib
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from src.models.user_model import User, APIKey, Subscription, PlanProduct, Plan
from src.models.tool_model import Tool
from src.database import redis_client

API_KEY_PREFIX = "ts_live_"
RATE_LIMIT_WINDOW = 60  # seconds

def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()

def create_api_key(user_id: str, tool_id: int, db: Session):
    """
    Generate an API key and store only its hash.
    Returns the raw key ONLY once.
    """

    if not user_id or not tool_id:
        raise ValueError("user_id and tool_id are required")

    # Validate user exists
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise ValueError("User does not exist")

    # Validate tool exists
    tool = db.query(Tool).filter(Tool.id == tool_id).first()

    if not tool:
        raise ValueError("Tool does not exist")


    # Check if THIS USER already has a key for THIS TOOL
    key_exists = db.query(APIKey).filter(
        APIKey.user_id == user_id,
        APIKey.tool_id == tool_id
    ).first()

    if key_exists:
        raise ValueError("API key for this tool already exists")

    # Generate key
    raw_key = secrets.token_urlsafe(32)
    full_key = f"{API_KEY_PREFIX}{raw_key}"

    # Hash key before storing
    hashed_key = hash_key(full_key)

    api_key = APIKey(
        user_id=user_id,
        tool_id=tool_id,
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

def has_access_to_tool(db, key_id: str, tool_id: str):

    if not key_id or not tool_id:
        return False

    return db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.tool_id == tool_id,
        APIKey.is_active == True
    ).first() is not None


def check_subscription(db, user_id: str, tool_id: str):

    if not user_id or not tool_id:
        return False

    now = datetime.now(timezone.utc)

    return db.query(Subscription).join(
        PlanProduct,
        Subscription.plan_id == PlanProduct.plan_id
    ).filter(
        Subscription.user_id == user_id,
        Subscription.status == "active",
        Subscription.start_date <= now,
        Subscription.end_date >= now,
        PlanProduct.tool_id == tool_id
    ).first() is not None

def check_rate_limit(db, key_id: str) -> bool:
    """
    Checks whether the API key exceeded its plan rate limit.

    Returns:
        True  -> Request allowed
        False -> Rate limit exceeded / invalid access
    """

    if not key_id:
        return False

    # --------------------------------------------------
    # Fetch plan rate limit for the API key + tool access
    # --------------------------------------------------

    rate_limit = (
        db.query(Plan.rate_limit)
        .join(
            Subscription,
            Subscription.plan_id == Plan.id,
        )
        .join(
            PlanProduct,
            PlanProduct.plan_id == Plan.id,
        )
        .join(
            APIKey,
            APIKey.tool_id == PlanProduct.tool_id,
        )
        .filter(
            APIKey.id == key_id,
            APIKey.user_id == Subscription.user_id,
            APIKey.is_active.is_(True),
            Subscription.status == "active",
        )
        .scalar()
    )

    # No valid subscription / tool access / api key
    if rate_limit is None:
        return False
    # print(f"rate_limit: {rate_limit}")
    # --------------------------------------------------
    # Redis Rate Limiting
    # --------------------------------------------------

    redis_key = f"rate_limit:{key_id}"

    current_count = redis_client.get(redis_key)

    # First request in the window
    if current_count is None:

        redis_client.set(
            redis_key,
            1,
            ex=RATE_LIMIT_WINDOW,
        )

        return True

    current_count = int(current_count)

    # Rate limit exceeded
    if current_count >= rate_limit:
        return False

    # Increment request count
    redis_client.incr(redis_key)

    return True
