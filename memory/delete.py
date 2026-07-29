from memory.chroma_client import collection
from memory.record_store import delete_records


def delete_memory(
        memory_id):

    collection.delete(

        ids=[
            memory_id
        ]

    )
    delete_records([memory_id])

    return {

        "deleted": memory_id

    }
