"""Compatibility boundary for legacy Ollama-powered workflows.

The MCP-facing Beta-1 path is provider-free: the host agent calls
``memcoder_prepare`` and ``memcoder_record``.  These older helpers remain
available only for installations that explicitly opt into ``memcoder[ollama]``.
"""


def get_ollama():
    """Import Ollama only when a legacy Ollama workflow is invoked."""
    try:
        import ollama
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "This legacy workflow requires the optional Ollama integration. "
            "Install 'memcoder[ollama]' and run Ollama, or use the "
            "provider-free memcoder_prepare/memcoder_record MCP tools."
        ) from error

    return ollama
