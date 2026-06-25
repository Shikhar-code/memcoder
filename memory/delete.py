from memory.chroma_client import collection


def delete_memory(
        memory_id):

    collection.delete(

        ids=[
            memory_id
        ]

    )

    return {

        "deleted": memory_id

    }