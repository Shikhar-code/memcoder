def validate_profile(profile):
    email = profile["email"].strip()
    return {"email": email, "display_name": profile.get("display_name", "")}
