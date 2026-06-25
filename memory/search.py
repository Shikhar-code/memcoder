from memory.embedder import embed
from memory.chroma_client import collection


def search_memory(
        query=None,
        query_embedding=None,
        k=3,
        memory_type=None,
        agent_id="human"):

    filters = []

    if memory_type is not None:

        filters.append(

            {
                "type": memory_type
            }

        )

    filters.append(

        {
            "$or": [

                {
                    "owner": "shared"
                },

                {
                    "owner": agent_id
                }

            ]
        }

    )

    if len(filters) == 1:

        where = filters[0]

    else:

        where = {

            "$and": filters

        }

    if query_embedding is None:

        query_embedding = embed(
            query
        )

    results = collection.query(

        query_embeddings=[
            query_embedding
        ],

        n_results=k,

        where=where

    )

    memories = results["metadatas"][0]
    distances = results["distances"][0]

    output = []

    for memory, distance in zip(
            memories,
            distances):

        output.append({

            "id":
                memory.get(
                    "hash",
                    ""
                ),

            "task":
                memory.get(
                    "task",
                    ""
                ),

            "files":
                memory.get(
                    "files",
                    []
                ),

            "summary":
                memory.get(
                    "summary",
                    ""
                ),

            "solution":
                memory.get(
                    "solution",
                    ""
                ),

            "importance":
                memory.get(
                    "importance",
                    0
                ),

            "type":
                memory.get(
                    "type",
                    "experience"
                ),

            "owner":
                memory.get(
                    "owner",
                    "shared"
                ),

            "confidence":
                memory.get(
                    "confidence",
                    1.0
                ),

            "frequency":
                memory.get(
                    "frequency",
                    1
                ),

            "score":
                distance

        })

    return output