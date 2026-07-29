from memory.chroma_client import collection
from memory.record_store import delete_records


def delete_memories(
        ids,
        verbose=False):

    if len(ids) == 0:
        if verbose:
            print("Nothing to delete.")
            return

    collection.delete(
        ids=ids
    )
    delete_records(ids)

    if verbose:

        print(
            f"Deleted {len(ids)} memories."
        )
