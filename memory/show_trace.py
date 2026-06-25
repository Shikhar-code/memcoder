import session.debug_state as debug_state


def show_trace():

    results = debug_state.last_retrieval

    if results is None:

        print()
        print("No previous query.")
        print()

        return

    print()

    for category in results:

        print(category.upper())

        for memory in results[category]:

            if category == "reflections":

                label = memory["summary"]

            elif category == "principles":

                label = memory["summary"]

            else:

                label = memory["task"]

            print(

                label,

                "| score:",

                round(memory["score"], 3)

            )

        print()