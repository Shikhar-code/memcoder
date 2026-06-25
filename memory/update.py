from memory.mutate import mutate_memory


def update_memory(
        memory_id,
        **updates):

    def updater(memory):

        memory.update(
            updates
        )

    return mutate_memory(

        memory_id,

        updater

    )