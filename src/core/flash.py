def flash(request, message: str, category: str = "info"):
    if "flash_messages" not in request.session:
        request.session["flash_messages"] = []

    request.session["flash_messages"].append(
        {"message": message, "category": category}
    )
