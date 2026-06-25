def budget_context(context, max_chars=3000):

    if len(context) <= max_chars:
        return context

    return (
        context[:max_chars]
        + "\n\n[CONTEXT TRUNCATED]"
    )