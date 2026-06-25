from memory.chroma_client import collection


def clear_owner(owner):
    """
    Delete every memory owned by the specified agent.

    This is primarily intended for development,
    testing and examples where a clean workspace
    is useful.

    Parameters
    ----------
    owner : str
        Agent owner ID.

    Returns
    -------
    int
        Number of memories deleted.
    """

    results = collection.get(
        where={
            "owner": owner
        }
    )

    if len(results["ids"]) == 0:
        return 0

    collection.delete(
        ids=results["ids"]
    )

    return len(results["ids"])