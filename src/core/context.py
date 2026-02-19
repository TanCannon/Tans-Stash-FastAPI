from src.core.params import params
from datetime import datetime
def get_global_context(request):
    flash_messages = request.session.pop("flash_messages", [])

    return {
        "params": params,
        "flash_messages": flash_messages,
        "current_year": datetime.now().year
    }

