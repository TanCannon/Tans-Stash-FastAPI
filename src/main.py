import os
from dotenv import load_dotenv

from fastapi import FastAPI, Request
from starlette import status
from .database import engine, Base
from .models.post_model import Post  
from .models.contact_model import Contact  
from .models.comment_model import Comment  
from .models.tool_model import Tool  
from .models.user_usage_model import ToolUsage  
# from .models import Base

# from .router import auth, todos, admin, user
from .routers import register_api_routers
from .routers import register_page_routers

from starlette.middleware.sessions import SessionMiddleware
#using for the frontend
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from src.filters import register_filters

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