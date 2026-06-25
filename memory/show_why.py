import session.debug_state as debug_state


def show_why():

    results = debug_state.last_retrieval

    if results is None:

        print()
        print("No previous query.")
        print()

        return

    print()

    print("EXPERIENCES")

    for memory in results["experiences"]:

        print("-", memory["task"])

    print()

    print("MISTAKES")

    for memory in results["mistakes"]:

        print("-", memory["task"])

    print()

    print("PRINCIPLES")

    for memory in results["principles"]:

        print("-", memory["summary"])

    print()

    print("REFLECTIONS")

    for memory in results["reflections"]:

        print("-", memory["summary"])

    print()