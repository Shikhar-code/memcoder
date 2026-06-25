from memory.search import search_memory
from memory.embedder import embed


def hierarchical_search(
        problem,
        agent_id="human"):

    query_embedding = embed(
        problem
    )

    return {

        "experiences":

        search_memory(

            query_embedding=query_embedding,

            k=5,

            memory_type="experience",

            agent_id=agent_id

        ),

        "mistakes":

        search_memory(

            query_embedding=query_embedding,

            k=3,

            memory_type="mistake",

            agent_id=agent_id

        ),

        "principles":

        search_memory(

            query_embedding=query_embedding,

            k=2,

            memory_type="principle",

            agent_id=agent_id

        ),

        "reflections":

        search_memory(

            query_embedding=query_embedding,

            k=2,

            memory_type="reflection",

            agent_id=agent_id

        )

    }