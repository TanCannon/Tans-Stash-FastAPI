from utils_for_unit_test import *

import hashlib

from src.models.user_model import APIKey
from src.services.api_key_service import create_api_key, API_KEY_PREFIX

def test_create_api_key_stores_hashed_key(db):
    user_id = "user_123"

    # Call function
    generated_key = create_api_key(user_id, db)

    # Fetch from DB
    keys = db.query(APIKey).filter(APIKey.user_id == user_id).all()

    # 1. One key should be created
    assert len(keys) == 1

    db_key = keys[0]

    # 2. Returned key should have prefix
    assert generated_key.startswith(API_KEY_PREFIX)

    # 3. Hash in DB should NOT equal raw key
    assert db_key.key_hash != generated_key

    # 4. Hash should match computed hash
    expected_hash = hashlib.sha256(generated_key.encode()).hexdigest()
    assert db_key.key_hash == expected_hash

    # 5. Key should be active
    assert db_key.is_active is True