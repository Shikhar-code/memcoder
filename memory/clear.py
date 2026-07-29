from memory.chroma_client import collection
from memory.record_store import delete_owner


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

    if results["ids"]:
        collection.delete(ids=results["ids"])
    durable_count = delete_owner(owner)
    return max(len(results["ids"]), durable_count)
