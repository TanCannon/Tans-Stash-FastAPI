from .api import posts_api

def register_api_routers(app):
    app.include_router(posts_api.router)