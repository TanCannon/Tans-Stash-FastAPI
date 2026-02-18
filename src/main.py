import os
from dotenv import load_dotenv

from fastapi import FastAPI
from .database import engine, Base
from .models.post_model import Post  
from .models.contact_model import Contact  
from .models.comment_model import Comment  
from .models.tool_model import Tool  
from .models.user_usage_model import ToolUsage  
# from .models import Base

# from .router import auth, todos, admin, user
from .routers import register_api_routers

from starlette.middleware.sessions import SessionMiddleware
#using for the frontend
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import RedirectResponse


from starlette import status
 
app = FastAPI()

load_dotenv()
# Session middleware (ONLY used by pages)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY")
)

Base.metadata.create_all(bind=engine)

#registering routers
register_api_routers(app)

@app.get('/', status_code=status.HTTP_200_OK)
async def hello_world():
    return {'message':'hello world'}