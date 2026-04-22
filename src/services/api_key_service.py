import secrets
import hashlib
from sqlalchemy.orm import Session

from src.models.user_model import APIKey

API_KEY_PREFIX = "ts_live_"

def create_api_key(user_id: str, db: Session):
    """
    Generated a api key and stores the hashed version of it in db.
    """
    raw_key = secrets.token_urlsafe(32)

    # Full API key
    full_key = f"{API_KEY_PREFIX}{raw_key}"

    hashed_key = hashlib.sha256(full_key.encode()).hexdigest()

    api_key = APIKey(
        user_id = user_id,
        key_hash = hashed_key,
        is_active = True
    )

    db.add(api_key)
    db.commit()

    return full_key #return ONLY ONCE


