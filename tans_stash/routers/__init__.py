from .api import posts_api, contact_api

def register_api_routers(app):
    app.include_router(posts_api.router)
    app.include_router(contact_api.router)