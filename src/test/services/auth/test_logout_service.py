# test/services/auth/test_logout_service.py

from unittest.mock import Mock

from src.services.auth import logout_service


# ==========================================================
# Test: Logout with active refresh token
# Expected:
#   - Token gets revoked
#   - Transaction committed
#   - Success response returned
# ==========================================================
def test_logout_revokes_active_token():
    db = Mock()

    db_token = Mock()
    db_token.is_revoked = False

    db.query.return_value.filter.return_value.first.return_value = db_token

    result = logout_service(
        db=db,
        refresh_token="valid-refresh-token",
    )

    assert db_token.is_revoked is True

    db.commit.assert_called_once()

    assert result == {
        "success": True,
        "message": "Logged out successfully",
    }


# ==========================================================
# Test: Logout when token not found
# Expected:
#   - No commit performed
#   - Success response returned
# ==========================================================
def test_logout_when_token_not_found():
    db = Mock()

    db.query.return_value.filter.return_value.first.return_value = None

    result = logout_service(
        db=db,
        refresh_token="missing-token",
    )

    db.commit.assert_not_called()

    assert result == {
        "success": True,
        "message": "Logged out successfully",
    }


# ==========================================================
# Test: Logout when token already revoked
# Expected:
#   - Query returns nothing because service
#     only searches active tokens
#   - No commit performed
# ==========================================================
def test_logout_with_already_revoked_token():
    db = Mock()

    db.query.return_value.filter.return_value.first.return_value = None

    result = logout_service(
        db=db,
        refresh_token="revoked-token",
    )

    db.commit.assert_not_called()

    assert result == {
        "success": True,
        "message": "Logged out successfully",
    }


# ==========================================================
# Test: Correct refresh token used in query
# Expected:
#   - Service queries database once
# ==========================================================
def test_logout_queries_database():
    db = Mock()

    db.query.return_value.filter.return_value.first.return_value = None

    logout_service(
        db=db,
        refresh_token="test-token",
    )

    db.query.assert_called_once()
