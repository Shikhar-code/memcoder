def build_problem_description(task):
    """
    For vector retrieval we want the actual user problem,
    not a long prompt explaining how retrieval should work.

    Embedding models work best when they embed the problem itself.
    """

    return task.strip()