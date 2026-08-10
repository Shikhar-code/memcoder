"""Lazy public exports for MemCoder's provider-free cognition API."""

__all__ = [
    "checkpoint_cognition",
    "intervene_cognition",
    "plan_cognition",
    "prepare_cognition",
    "record_cognition",
    "start_cognition",
    "task_state_cognition",
    "verify_cognition",
]


def __getattr__(name):
    if name in __all__:
        from api import cognition
        return getattr(cognition, name)
    raise AttributeError(f"module 'memcoder' has no attribute {name!r}")
