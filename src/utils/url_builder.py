from enum import Enum

from fastapi import Request


def build_url(request: Request, route_name: str, **params) -> str:
    """
    Build an absolute URL for a named route, with optional query parameters.

    Query parameters whose value is ``None`` are omitted, so optional filters
    can be passed straight through without checking them first. ``Enum`` values
    are converted to their underlying ``.value``. Values are URL-encoded by
    Starlette.

    Args:
        request: The current request, used to resolve the route and base URL.
        route_name: The name of the target route (the ``name=`` given to the
            route decorator, or the function name by default).
        **params: Query parameters to append, as keyword arguments.

    Returns:
        The absolute URL as a string, including the query string if any
        parameters remain after filtering.

    Raises:
        starlette.routing.NoMatchFound: If ``route_name`` does not exist.
    Example:
        >>> build_url(request, "dashboard", page=2, post_status=PostStatus.DRAFT)
        'http://localhost:8000/dashboard?page=2&post_status=draft'

        >>> build_url(request, "dashboard", page=2, post_status=None)
        'http://localhost:8000/dashboard?page=2'
    """
    # Drop unset params and unwrap enums so callers can pass them as-is.
    query = {
        key: value.value if isinstance(value, Enum) else value
        for key, value in params.items()
        if value is not None
    }

    # include_query_params handles the ?/& separators and URL-encoding.
    return str(request.url_for(route_name).include_query_params(**query))
