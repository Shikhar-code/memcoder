"""Public MemCoder SDK exports, loaded only when an SDK symbol is requested."""

__all__ = [
    "MemCoderAgent",
    "banner",
    "show",
    "show_results",
    "show_answer",
    "show_trace"
]


def __getattr__(name):
    """Avoid loading retrieval dependencies for CLI-only automation hosts."""
    if name == "MemCoderAgent":
        from client.agent import MemCoderAgent
        return MemCoderAgent

    if name in {"banner", "show", "show_results", "show_answer", "show_trace"}:
        from client import display
        return getattr(display, name)

    raise AttributeError(f"module 'memcoder' has no attribute {name!r}")
