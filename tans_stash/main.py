from fastapi import FastAPI
from .database import engine, Base
from .models.post_model import Post  
from .models.contact_model import Contact  
from .models.comment_model import Comment  
from .models.tool_model import Tool  
from .models.user_usage_model import ToolUsage  
# from .models import Base

# from .router import auth, todos, admin, user

#using for the frontend
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import RedirectResponse

from starlette import status
 
app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get('/', status_code=status.HTTP_200_OK)
async def hello_world():
    return {'message':'hello world'}