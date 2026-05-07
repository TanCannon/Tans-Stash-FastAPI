from src.test.conftest import db, pytest
from src.models.user_model import User, APIKey
from src.services.api_key_service import create_api_key, hash_key, API_KEY_PREFIX

# 1. Success Case
def test_create_api_key_success(db):
    user = User(id="user123", username="user123", email="user123@mail.com", password_hash="12345")
    db.add(user)
    db.commit()

    full_key = create_api_key(user.id, db)

    assert full_key is not None
    assert full_key.startswith(API_KEY_PREFIX)

    stored = db.query(APIKey).filter(APIKey.user_id == user.id).first()

    assert stored is not None
    assert stored.key_hash == hash_key(full_key)
    assert stored.is_active is True

# 2. User Does Not Exist
def test_create_api_key_user_not_found(db):
    with pytest.raises(ValueError, match="User does not exist"):
        create_api_key("invalid_user", db)
    
# 3. Raw Key NOT Stored
def test_raw_key_not_stored(db):
    user = User(id="user123", username="user123", email="user123@mail.com", password_hash="12345")
    db.add(user)
    db.commit()

    full_key = create_api_key(user.id, db)

    stored = db.query(APIKey).first()

    assert stored.key_hash != full_key

# 4. Multiple Keys Unique
def test_multiple_keys_unique(db):
    user = User(id="user123", username="user123", email="user123@mail.com", password_hash="12345")
    db.add(user)
    db.commit()

    key1 = create_api_key(user.id, db)
    key2 = create_api_key(user.id, db)

    assert key1 != key2

    keys = db.query(APIKey).filter(APIKey.user_id == user.id).all()

    assert len(keys) == 2
    assert len(set(k.key_hash for k in keys)) == 2

# 5. Hash Consistency
def test_hash_consistency(db):
    user = User(id="user123", username="user123", email="user123@mail.com", password_hash="12345")
    db.add(user)
    db.commit()

    full_key = create_api_key(user.id, db)

    stored = db.query(APIKey).first()

    assert hash_key(full_key) == stored.key_hash

# 6. API Key Format
def test_api_key_format(db):
    user = User(id="user123", username="user123", email="user123@mail.com", password_hash="12345")
    db.add(user)
    db.commit()

    full_key = create_api_key(user.id, db)

    assert full_key.startswith(API_KEY_PREFIX)  # prefix
    assert len(full_key) > 40