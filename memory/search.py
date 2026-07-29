from memory.embedder import embed
from memory.chroma_client import collection
from memory.records import record_id
from memory.provenance import trace
from memory.proof import build_proof


def search_memory(
        query=None,
        query_embedding=None,
        k=3,
        memory_type=None,
        agent_id="human",
        include_shared=True):

    filters = []

    if memory_type is not None:

        filters.append(

            {
                "type": memory_type
            }

        )

    if include_shared:
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
    else:
        filters.append(
            {
                "owner": agent_id
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

        result = {

            "id":
                record_id(memory),

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

            "verification":
                 memory.get(
                   "verification",
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

            "record_state": memory.get("record_state", "trusted"),

            "revision": memory.get("revision", 1),

            "environment": memory.get("environment", ""),

            "validity_reason": memory.get("validity_reason", ""),

            "provenance": trace(record_id(memory), owner=memory.get("owner")),

            "source":
                memory.get(
                    "source",
                    ""
                ),

            "source_experience_id":
                memory.get(
                    "source_experience_id",
                    ""
                ),

            "skill_definition":
                memory.get(
                    "skill_definition",
                    ""
                ),

            "supporting_experience_ids":
                memory.get(
                    "supporting_experience_ids",
                    ""
                ),

            "supporting_principle_ids":
                memory.get(
                    "supporting_principle_ids",
                    ""
                ),

            "score": distance
        }
        result["proof"] = build_proof(result)
        output.append(result)

    return output
