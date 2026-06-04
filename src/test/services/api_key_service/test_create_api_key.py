from src.test.conftest import db, pytest
from src.models.user_model import User, APIKey
from src.models.tool_model import Tool
from src.services.api_key_service import create_api_key, hash_key, API_KEY_PREFIX

# 1. Success Case
def test_create_api_key_success(db):
    user = User(
        id="user123",
        username="user123",
        email="user123@mail.com",
        password_hash="12345"
    )

    tool = Tool(
        slug="weather-api",
        name="Weather API"
    )

    db.add_all([user, tool])
    db.commit()

    full_key = create_api_key(user.id, tool.id, db)

    assert full_key is not None
    assert full_key.startswith(API_KEY_PREFIX)

    stored = db.query(APIKey).filter(
        APIKey.user_id == user.id,
        APIKey.tool_id == tool.id
    ).first()

    assert stored is not None
    assert stored.key_hash == hash_key(full_key)
    assert stored.is_active is True


# 2. User Does Not Exist
def test_create_api_key_user_not_found(db):
    tool = Tool(
        slug="weather-api",
        name="Weather API"
    )

    db.add(tool)
    db.commit()

    with pytest.raises(ValueError, match="User does not exist"):
        create_api_key("invalid_user", tool.id, db)


# 3. Tool Does Not Exist
def test_create_api_key_tool_not_found(db):
    user = User(
        id="user123",
        username="user123",
        email="user123@mail.com",
        password_hash="12345"
    )

    db.add(user)
    db.commit()

    with pytest.raises(ValueError, match="Tool does not exist"):
        create_api_key(user.id, 999, db)


# 4. Raw Key NOT Stored
def test_raw_key_not_stored(db):
    user = User(
        id="user123",
        username="user123",
        email="user123@mail.com",
        password_hash="12345"
    )

    tool = Tool(
        slug="weather-api",
        name="Weather API"
    )

    db.add_all([user, tool])
    db.commit()

    full_key = create_api_key(user.id, tool.id, db)

    stored = db.query(APIKey).first()

    assert stored.key_hash != full_key


# 5. Duplicate Key For Same Tool
def test_duplicate_api_key_same_tool(db):
    user = User(
        id="user123",
        username="user123",
        email="user123@mail.com",
        password_hash="12345"
    )

    tool = Tool(
        slug="weather-api",
        name="Weather API"
    )

    db.add_all([user, tool])
    db.commit()

    create_api_key(user.id, tool.id, db)

    with pytest.raises(ValueError, match="API key for this tool already exists"):
        create_api_key(user.id, tool.id, db)


# 6. Different Tools Allowed
def test_multiple_api_keys_different_tools(db):
    user = User(
        id="user123",
        username="user123",
        email="user123@mail.com",
        password_hash="12345"
    )

    tool1 = Tool(
        slug="weather-api",
        name="Weather API"
    )

    tool2 = Tool(
        slug="maps-api",
        name="Maps API"
    )

    db.add_all([user, tool1, tool2])
    db.commit()

    key1 = create_api_key(user.id, tool1.id, db)
    key2 = create_api_key(user.id, tool2.id, db)

    assert key1 != key2

    keys = db.query(APIKey).filter(
        APIKey.user_id == user.id
    ).all()

    assert len(keys) == 2


# 7. Hash Consistency
def test_hash_consistency(db):
    user = User(
        id="user123",
        username="user123",
        email="user123@mail.com",
        password_hash="12345"
    )

    tool = Tool(
        slug="weather-api",
        name="Weather API"
    )

    db.add_all([user, tool])
    db.commit()

    full_key = create_api_key(user.id, tool.id, db)

    stored = db.query(APIKey).first()

    assert hash_key(full_key) == stored.key_hash


# 8. API Key Format
def test_api_key_format(db):
    user = User(
        id="user123",
        username="user123",
        email="user123@mail.com",
        password_hash="12345"
    )

    tool = Tool(
        slug="weather-api",
        name="Weather API"
    )

    db.add_all([user, tool])
    db.commit()

    full_key = create_api_key(user.id, tool.id, db)

    assert full_key.startswith(API_KEY_PREFIX)
    assert len(full_key) > 40
