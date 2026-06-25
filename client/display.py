from textwrap import fill


LINE = "=" * 60
SEP = "-" * 60


def banner(title):

    print()
    print(LINE)
    print(title)
    print(LINE)
    print()


def _section(name, value):

    print(name)

    print(fill(str(value), width=70))

    print()


def show(memory):

    if memory is None:

        print("No memory.")

        return

    print(SEP)

    print(memory["type"].title())

    print(SEP)

    _section("Task", memory["task"])

    _section("Summary", memory["summary"])

    _section("Solution", memory["solution"])

    _section("Owner", memory.get("owner", "shared"))

    print()


def show_results(results):

    if len(results) == 0:

        print("No memories found.")

        return

    print(f"Found {len(results)} memories.\n")

    for memory in results:

        show(memory)


def show_answer(result):

    banner("Solution")

    print(result["answer"])


def show_trace(trace):

    banner("Hierarchical Retrieval")

    for group in [

        "experiences",

        "mistakes",

        "principles",

        "reflections"

    ]:

        print(group.upper())

        print()

        if len(trace[group]) == 0:

            print("  (none)\n")

            continue

        for memory in trace[group]:

            print(f"• {memory['task']}")

        print()