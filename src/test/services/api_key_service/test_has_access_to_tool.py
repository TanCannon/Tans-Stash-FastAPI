from src.models.tool_model import Tool
from src.models.user_model import Plan, PlanProduct, Subscription, APIKey, User
from src.services.api_key_service import has_access_to_tool

# 1. Test: Empty Inputs
def test_has_access_empty_inputs(db):
    assert has_access_to_tool(db, "", "") is False
    assert has_access_to_tool(db, "abc", "") is False
    assert has_access_to_tool(db, "", "tool1") is False


# 2. Test: API Key Has Access
def test_has_access_success(db):

    user = User(
        id="user1",
        username="user1",
        email="user1@mail.com",
        password_hash="123"
    )

    tool = Tool(
        id=1,
        slug="tool1",
        name="Tool1"
    )

    db.add_all([user, tool])
    db.commit()

    api_key = APIKey(
        user_id=user.id,
        tool_id=tool.id,
        key_hash="hashed_key_123",
        is_active=True
    )

    db.add(api_key)
    db.commit()

    result = has_access_to_tool(
        db,
        "hashed_key_123",
        tool.id
    )

    assert result is True


# 3. Test: API Key Does Not Exist
def test_has_access_invalid_key(db):

    tool = Tool(
        id=1,
        slug="tool1",
        name="Tool1"
    )

    db.add(tool)
    db.commit()

    result = has_access_to_tool(
        db,
        "invalid_key",
        tool.id
    )

    assert result is False


# 4. Test: Inactive API Key
def test_has_access_inactive_key(db):

    user = User(
        id="user1",
        username="user1",
        email="user1@mail.com",
        password_hash="123"
    )

    tool = Tool(
        id=1,
        slug="tool1",
        name="Tool1"
    )

    db.add_all([user, tool])
    db.commit()

    api_key = APIKey(
        user_id=user.id,
        tool_id=tool.id,
        key_hash="hashed_key_123",
        is_active=False
    )

    db.add(api_key)
    db.commit()

    result = has_access_to_tool(
        db,
        "hashed_key_123",
        tool.id
    )

    assert result is False


# 5. Test: API Key Used For Wrong Tool
def test_has_access_wrong_tool(db):

    user = User(
        id="user1",
        username="user1",
        email="user1@mail.com",
        password_hash="123"
    )

    tool1 = Tool(
        id=1,
        slug="tool1",
        name="Tool1"
    )

    tool2 = Tool(
        id=2,
        slug="tool2",
        name="Tool2"
    )

    db.add_all([user, tool1, tool2])
    db.commit()

    api_key = APIKey(
        user_id=user.id,
        tool_id=tool1.id,
        key_hash="hashed_key_123",
        is_active=True
    )

    db.add(api_key)
    db.commit()

    result = has_access_to_tool(
        db,
        "hashed_key_123",
        tool2.id
    )

    assert result is False


# 6. Test: Multiple Users Isolation
def test_has_access_multiple_users(db):

    user1 = User(
        id="user1",
        username="user1",
        email="user1@mail.com",
        password_hash="123"
    )

    user2 = User(
        id="user2",
        username="user2",
        email="user2@mail.com",
        password_hash="456"
    )

    tool = Tool(
        id=1,
        slug="tool1",
        name="Tool1"
    )

    db.add_all([user1, user2, tool])
    db.commit()

    api_key = APIKey(
        user_id=user1.id,
        tool_id=tool.id,
        key_hash="hashed_key_123",
        is_active=True
    )

    db.add(api_key)
    db.commit()

    result = has_access_to_tool(
        db,
        "another_users_key",
        tool.id
    )

    assert result is False


# 7. Test: Multiple API Keys For Different Tools
def test_has_access_multiple_keys(db):

    user = User(
        id="user1",
        username="user1",
        email="user1@mail.com",
        password_hash="123"
    )

    tool1 = Tool(
        id=1,
        slug="tool1",
        name="Tool1"
    )

    tool2 = Tool(
        id=2,
        slug="tool2",
        name="Tool2"
    )

    db.add_all([user, tool1, tool2])
    db.commit()

    key1 = APIKey(
        user_id=user.id,
        tool_id=tool1.id,
        key_hash="key_tool_1",
        is_active=True
    )

    key2 = APIKey(
        user_id=user.id,
        tool_id=tool2.id,
        key_hash="key_tool_2",
        is_active=True
    )

    db.add_all([key1, key2])
    db.commit()

    assert has_access_to_tool(db, "key_tool_1", tool1.id) is True

    assert has_access_to_tool(db, "key_tool_1", tool2.id) is False

    assert has_access_to_tool(db, "key_tool_2", tool2.id) is True
