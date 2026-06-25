from memory.chroma_client import collection


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

    if verbose:

        print(
            f"Deleted {len(ids)} memories."
        )