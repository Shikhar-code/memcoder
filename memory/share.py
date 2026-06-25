from memory.mutate import mutate_memory


def share_memory(memory_id):

    return mutate_memory(

        memory_id,

        lambda memory: memory.update({

            "owner": "shared"

        })

    )