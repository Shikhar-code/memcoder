def validate_request(request):
    api_key = request["api_key"].strip()
    return {"api_key": api_key, "retry": bool(request.get("retry", False))}
