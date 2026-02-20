import os
from dotenv import load_dotenv

from fastapi import FastAPI, Request
from .database import engine, Base

from .routers import register_api_routers
from .routers import register_page_routers

from starlette.middleware.sessions import SessionMiddleware
#using for the frontend
from fastapi.staticfiles import StaticFiles

from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.templates import templates
from src.core.params import params
from src.core.context import get_global_context

app = FastAPI()

load_dotenv()
# Session middleware (ONLY used by pages)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY")
)


@app.on_event("startup")
async def startup():
    try:
        Base.metadata.create_all(bind=engine)
        print("Database connected successfully.")
    except Exception as e:
        print("Database not available. App starting without DB.")

#setting up static files directory
app.mount("/static", StaticFiles(directory="src/static"), name="static")

#registering routers
register_api_routers(app)

#register page routers
register_page_routers(app)

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: StarletteHTTPException):
    context = get_global_context(request)
    context.update({
        "request": request,
        "params": params,
    })

    return templates.TemplateResponse(
        "404.html",
        context,
        status_code=404,
    )

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    context = get_global_context(request)
    context.update({
        "request": request,
        "params": params,
    })

    return templates.TemplateResponse(
        "500.html",
        context,
        status_code=500,
    )
