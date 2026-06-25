from memory.search import search_memory


def show_search(
        query,
        k=5):

    memories = search_memory(
        query,
        k=k
    )

    for i, memory in enumerate(
            memories,
            start=1):

        print()
        print("=" * 70)
        print(f"Memory {i}")
        print()

        print("Task:")
        print(memory["task"])

        print()
        print("Summary:")
        print(memory["summary"])

        print()
        print("Solution:")
        print(memory["solution"])

        print()