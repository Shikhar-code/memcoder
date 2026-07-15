def validate_profile(profile):
    if "profile_name" not in profile or profile["profile_name"] is None:
        raise ValueError("profile_name is required")

    val = profile["profile_name"]
    if not isinstance(val, str) or val == "" or val.isspace():
        raise ValueError("profile_name is required")

    profile_name = val.strip()
    region = profile.get("region", "default").strip()

    return {
        "profile_name": profile_name,
        "region": region
    }
