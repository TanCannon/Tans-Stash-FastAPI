from fastapi.templating import Jinja2Templates

from src.filters import register_filters

templates = Jinja2Templates(directory="src/templates")
# register filters
register_filters(templates)