from .api import posts_api, contact_api, ascii_tree_to_zip_api, dashboard_api, analytics_api, search_api

from .pages import home, blog, about

def register_api_routers(app):
    app.include_router(posts_api.router)
    app.include_router(contact_api.router)
    app.include_router(ascii_tree_to_zip_api.router)
    app.include_router(dashboard_api.router)
    app.include_router(analytics_api.router)
    app.include_router(search_api.router)

def register_page_routers(app):
    app.include_router(home.router)
    app.include_router(blog.router)
    app.include_router(about.router)