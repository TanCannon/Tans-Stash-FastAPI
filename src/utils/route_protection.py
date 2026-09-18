PROTECTED_ROUTES = [
    "/private"   # all my product APIs
]

def is_protected_route(path: str):
    return any(path.startswith(route) for route in PROTECTED_ROUTES)
