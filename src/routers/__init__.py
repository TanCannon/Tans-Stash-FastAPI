from .api import posts_api, contact_api, ascii_tree_to_zip_api, dashboard_api, analytics_api, search_api, auth_api, plan_api

from .pages import home, blog, about, disclaimer, faq, privacy, terms, tools, contact, login, dashboard, search, sitemap, robots_txt, favicon_ico, ads_txt

def register_api_routers(app):
    app.include_router(posts_api.router)
    app.include_router(contact_api.router)
    app.include_router(ascii_tree_to_zip_api.router)
    app.include_router(dashboard_api.router)
    app.include_router(analytics_api.router)
    app.include_router(search_api.router)
    app.include_router(auth_api.router)
    app.include_router(plan_api.router)

def register_page_routers(app):
    app.include_router(home.router)
    app.include_router(blog.router)
    app.include_router(about.router)
    app.include_router(disclaimer.router)
    app.include_router(faq.router)
    app.include_router(privacy.router)
    app.include_router(terms.router)
    app.include_router(tools.router)
    app.include_router(contact.router)
    app.include_router(login.router)
    app.include_router(dashboard.router)
    app.include_router(search.router)
    app.include_router(sitemap.router)
    app.include_router(robots_txt.router)
    app.include_router(favicon_ico.router)
    app.include_router(ads_txt.router)