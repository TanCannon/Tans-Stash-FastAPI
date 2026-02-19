def get_global_context(request):
    flash_messages = request.session.pop("flash_messages", [])

    return {
        "flash_messages": flash_messages
    }
