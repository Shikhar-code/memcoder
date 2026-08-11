"""Lazy public exports for MemCoder's provider-free cognition API."""

__all__ = [
    "autopilot_control_cognition",
    "autopilot_event_cognition",
    "certify_host_cognition",
    "checkpoint_cognition",
    "compile_skill_cognition",
    "compose_skills_cognition",
    "cognition_contract_cognition",
    "dream_cognition",
    "evolve_skill_cognition",
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
    "skill_credit_cognition",
    "task_state_cognition",
    "token_ledger_cognition",
    "verify_cognition",
    "utility_feedback_cognition",
]


def __getattr__(name):
    if name in __all__:
        from api import cognition
        return getattr(cognition, name)
    raise AttributeError(f"module 'memcoder' has no attribute {name!r}")
