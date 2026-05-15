import os
from dotenv import load_dotenv

from fastapi import Depends, FastAPI, Request
from contextlib import asynccontextmanager

from fastapi.security import APIKeyHeader
from .database import engine, Base

from .routers import register_api_routers
from .routers import register_page_routers

from starlette.middleware.sessions import SessionMiddleware
#using for the frontend
from fastapi.staticfiles import StaticFiles

from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse

from src.core.templates import templates
from src.core.params import params
from src.core.context import get_global_context

#enables compression of responses
from fastapi.middleware.gzip import GZipMiddleware

#enable CORS
from fastapi.middleware.cors import CORSMiddleware

from src.middleware.api_gateway_middleware import APIGatewayMiddleware

@asynccontextmanager
async def lifespan(app):
    try:
        Base.metadata.create_all(bind=engine)
        print("Database connected successfully.")
    except Exception:
        print("Database not available. App starting without DB.")

    yield  # THIS IS MANDATORY

    # optional shutdown logic
    print("App shutting down...")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    GZipMiddleware,
    minimum_size=500
)


app.add_middleware(APIGatewayMiddleware)

# Read allowed origins from env, fallback to common dev hosts
allowed_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
# Session middleware (ONLY used by pages)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY"),
    https_only=False, #by default the session cookies are send over https only, doing this ensures it runs locally too
    same_site="lax" #change it to none in production
)

#setting up static files directory
app.mount("/static", StaticFiles(directory="src/static"), name="static")

#registering routers
register_api_routers(app)


api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)
#example: ts_live_QaRsPqugcvpsDM-shnNpgPY6Ts1_gpFu8KcK2w7lBIM
@app.get("/private/my-api")
def my_api(
    request: Request,
    api_key: str = Depends(api_key_header)  # 👈 just for Swagger
):
    user_id = request.state.user_id

    return {
        "message": "Hello u have reached the analytics service",
        "desc": "Provides usage analytics and metrics",
        "user_id": user_id
    }

#register page routers
register_page_routers(app)

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: StarletteHTTPException):
    # API routes → return JSON
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=404,
            content={"detail": exc.detail or "Not Found"}
        )
    
    # Frontend → return HTML
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
    # API routes → return JSON
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )

    # Frontend → return HTML
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
