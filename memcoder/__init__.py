"""Lazy public exports for MemCoder's provider-free cognition API."""

__all__ = [
    "checkpoint_cognition",
    "intervene_cognition",
    "project_accept_cognition",
    "project_handoff_cognition",
    "project_resurrect_cognition",
    "project_update_cognition",
    "plan_cognition",
    "prepare_cognition",
    "record_cognition",
    "retrieval_debug_cognition",
    "start_cognition",
    "task_state_cognition",
    "verify_cognition",
    "utility_feedback_cognition",
]


def __getattr__(name):
    if name in __all__:
        from api import cognition
        return getattr(cognition, name)
    raise AttributeError(f"module 'memcoder' has no attribute {name!r}")
