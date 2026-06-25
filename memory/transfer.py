from memory.mutate import mutate_memory


def transfer_memory(
        memory_id,
        owner):

    return mutate_memory(

        memory_id,

        lambda memory: memory.update({

            "owner": owner

        })

    )