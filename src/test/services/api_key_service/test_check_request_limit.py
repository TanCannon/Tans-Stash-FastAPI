from unittest.mock import MagicMock, patch
import pytest
from redis.exceptions import ConnectionError

from src.exceptions.redis_exceptions import (
    RedisUnavailableException,
)
from src.services.api_key_service import (
    check_request_limit,
)


# ======================================================
# Invalid key_id
# ======================================================

def test_check_request_limit_invalid_key_id(db):

    result = check_request_limit(
        db=db,
        key_id=""
    )

    assert result is False


# ======================================================
# No valid subscription / access
# ======================================================

@patch("src.services.api_key_service.redis_client")
def test_check_request_limit_no_access(
    mock_redis,
    db
):

    mock_query = MagicMock()
    mock_query.join.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.scalar.return_value = None

    db.query = MagicMock(return_value=mock_query)

    result = check_request_limit(
        db=db,
        key_id="test-key"
    )

    assert result is False

    mock_redis.incr.assert_not_called()


# ======================================================
# Unlimited plan
# ======================================================

@patch("src.services.api_key_service.redis_client")
def test_check_request_limit_unlimited_plan(
    mock_redis,
    db
):

    mock_query = MagicMock()

    mock_query.join.return_value = mock_query
    mock_query.filter.return_value = mock_query

    # request_limit <= 0 => unlimited
    mock_query.scalar.return_value = 0

    db.query = MagicMock(return_value=mock_query)

    result = check_request_limit(
        db=db,
        key_id="test-key"
    )

    assert result is True

    mock_redis.incr.assert_not_called()


# ======================================================
# First request in month
# ======================================================

@patch("src.services.api_key_service.redis_client")
def test_check_request_limit_first_request(
    mock_redis,
    db
):

    mock_query = MagicMock()

    mock_query.join.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.scalar.return_value = 100

    db.query = MagicMock(return_value=mock_query)

    # First request
    mock_redis.incr.return_value = 1

    result = check_request_limit(
        db=db,
        key_id="test-key"
    )

    assert result is True

    mock_redis.incr.assert_called_once()

    mock_redis.expire.assert_called_once()


# ======================================================
# Valid request within limit
# ======================================================

@patch("src.services.api_key_service.redis_client")
def test_check_request_limit_allowed_request(
    mock_redis,
    db
):

    mock_query = MagicMock()

    mock_query.join.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.scalar.return_value = 100

    db.query = MagicMock(return_value=mock_query)

    # Current usage = 50
    mock_redis.incr.return_value = 50

    result = check_request_limit(
        db=db,
        key_id="test-key"
    )

    assert result is True

    mock_redis.expire.assert_not_called()


# ======================================================
# Limit exceeded
# ======================================================

@patch("src.services.api_key_service.redis_client")
def test_check_request_limit_exceeded(
    mock_redis,
    db
):

    mock_query = MagicMock()

    mock_query.join.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.scalar.return_value = 100

    db.query = MagicMock(return_value=mock_query)

    # Request #101
    mock_redis.incr.return_value = 101

    result = check_request_limit(
        db=db,
        key_id="test-key"
    )

    assert result is False


# ======================================================
# Redis connection failure
# ======================================================

@patch("src.services.api_key_service.redis_client")
def test_check_request_limit_redis_failure(
    mock_redis,
    db
):

    mock_query = MagicMock()

    mock_query.join.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.scalar.return_value = 100

    db.query = MagicMock(return_value=mock_query)

    mock_redis.incr.side_effect = ConnectionError()

    with pytest.raises(
        RedisUnavailableException
    ):

        check_request_limit(
            db=db,
            key_id="test-key"
        )

