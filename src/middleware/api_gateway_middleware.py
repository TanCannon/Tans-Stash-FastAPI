import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from sqlalchemy.exc import SQLAlchemyError
from src.exceptions import RedisUnavailableException

from starlette.middleware.base import BaseHTTPMiddleware

from src.database import SessionLocal

from src.models.tool_model import Endpoint

from src.services.api_key_service import validate_api_key, has_access_to_tool, check_rate_limit, check_request_limit
from src.utils.route_protection import is_protected_route


logger = logging.getLogger(__name__)


class APIGatewayMiddleware(BaseHTTPMiddleware):
    def _validate_api_key(self, db, api_key: str):
        return validate_api_key(
            db=db,
            incoming_key=api_key
        )

    def _check_rate_limit(self, db, key_id: str):
        return check_rate_limit(
            db=db,
            key_id=key_id
        )

    def _check_request_limit(self, db, key_id: str):
        return check_request_limit(
            db=db,
            key_id=key_id
        )

    def _has_tool_access(
        self,
        db,
        key_id: str,
        tool_id: str
    ):

        return has_access_to_tool(
            db=db,
            key_id=key_id,
            tool_id=tool_id
        )

    def _get_tool_id(
        self,
        db,
        request_path: str
    ):

        return db.query(Endpoint.tool_id).filter(
            Endpoint.path == request_path
        ).scalar()

    def _attach_request_identity(
        self,
        request: Request,
        key_data: dict
    ):

        request.state.user_id = key_data["user_id"]
        request.state.api_key_id = key_data["api_key_id"]

    @staticmethod
    def _error_response(
        status_code: int,
        detail: str
    ):

        return JSONResponse(
            status_code=status_code,
            content={"detail": detail}
        )

    async def dispatch(self, request: Request, call_next):

        request_path = request.url.path

        # 1. Skip public routes
        if not is_protected_route(request_path):
            return await call_next(request)

        # 2. Check API key existence
        api_key = request.headers.get("x-api-key")

        if not api_key:
            return self._error_response(
                status_code=401,
                detail="API key missing"
            )

        db = SessionLocal()

        try:

            # 3. Validate API key
            key_data = self._validate_api_key(db, api_key)

            if not key_data:
                return self._error_response(
                    status_code=403,
                    detail="Invalid API key"
                )

            # 4. Rate limit validation
            is_allowed = self._check_rate_limit(
                db=db,
                key_id=key_data["api_key_id"]
            )

            if not is_allowed:
                return self._error_response(
                    status_code=429,
                    detail="Rate limit exceeded"
                )

            # 5. Endpoint → Tool mapping
            tool_id = self._get_tool_id(
                db=db,
                request_path=request_path
            )

            if not tool_id:
                logger.warning(
                    "Endpoint not mapped to tool",
                    extra={"path": request_path}
                )

                return self._error_response(
                    status_code=404,
                    detail="Endpoint not mapped to any tool"
                )

            # 6. Tool access validation
            has_access = self._has_tool_access(
                db=db,
                key_id=key_data["api_key_id"],
                tool_id=tool_id
            )

            if not has_access:
                return self._error_response(
                    status_code=403,
                    detail="Access denied for this API"
                )

            # 7. Plan limit validation
            can_request = self._check_request_limit(db=db, key_id=key_data["api_key_id"])
            
            if not can_request:
                 return self._error_response(
                    status_code=429,
                    detail="Monthly request limit exceeded"
                )

            # 8. Attach request identity
            self._attach_request_identity(request, key_data)
#            request.state.user_id = key_data["user_id"]
           # request.state.api_key_id = key_data["api_key_id"]

            return await call_next(request)

        # ==============================================
        # Redis Errors
        # ==============================================

        except RedisUnavailableException:

            logger.exception(
                "Redis service unavailable in API gateway middleware"
            )

            return self._error_response(
                status_code=503,
                detail="Service temporarily unavailable"
            )

        # ==============================================
        # Database Errors
        # ==============================================

        except SQLAlchemyError:

            logger.exception(
                "Database error in API gateway middleware"
            )

            return self._error_response(
                status_code=500,
                detail="Database error"
            )

        # ==============================================
        # Unexpected Errors
        # ==============================================

        except Exception:

            logger.exception(
                "Unexpected middleware error"
            )

            return self._error_response(
                status_code=500,
                detail="Internal server error"
            )  

        finally:
            db.close()

