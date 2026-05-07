from src.test.conftest import db
from src.models.user_model import User, APIKey
from src.services.api_key_service import validate_api_key, hash_key

# 1. Test: Valid API Key
def test_validate_api_key_success(db):
    raw_key = "my-secret-key"
    hashed = hash_key(raw_key)

    api_key = APIKey(
        key_hash=hashed,
        user_id='1',
        is_active=True
    )

    db.add(api_key)
    db.commit()

    result = validate_api_key(db, raw_key)

    assert result is not None
    assert result["user_id"] == '1'
    assert result["api_key_id"] == api_key.id

# 2. Test: Invalid API Key
def test_validate_api_key_not_found(db):
    result = validate_api_key(db, "wrong-key")

    assert result is None

# 3. Test: Inactive API Key
def test_validate_api_key_inactive(db):
    raw_key = "inactive-key"
    hashed = hash_key(raw_key)

    api_key = APIKey(
        key_hash=hashed,
        user_id='1',
        is_active=False
    )

    db.add(api_key)
    db.commit()

    result = validate_api_key(db, raw_key)

    assert result is None

# 4. Test: Hashing Consistency
def test_validate_api_key_hashing(db):
    raw_key = "secure-key"
    
    api_key = APIKey(
        key_hash=hash_key(raw_key),
        user_id='42',
        is_active=True
    )

    db.add(api_key)
    db.commit()

    # Try with same key → should work
    result = validate_api_key(db, raw_key)
    assert result is not None

    # Try with slightly different key → should fail
    result_wrong = validate_api_key(db, raw_key + "x")
    assert result_wrong is None

# 5. Test: Multiple Keys (Correct One Returned)
def test_validate_api_key_multiple_keys(db):
    key1 = "key1"
    key2 = "key2"

    db.add_all([
        APIKey(key_hash=hash_key(key1), user_id='1', is_active=True),
        APIKey(key_hash=hash_key(key2), user_id='2', is_active=True),
    ])
    db.commit()

    result = validate_api_key(db, key2)

    assert result["user_id"] == '2'