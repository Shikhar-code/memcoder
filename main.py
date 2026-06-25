import threading
import time

from agent.problem_solver import solve_problem

from memory.conversation_learner import (
    learn_from_conversation
)

from memory.consolidate_and_replace import (
    consolidate_and_replace
)

from memory.stats import memory_stats
from memory.show_search import show_search
from memory.show_why import show_why
from memory.show_trace import show_trace
from session.chat_history import (
    add_turn,
    get_recent_history,
    clear_history
)

from cache.query_cache import (
    query_cache
)
from memory.embedder import get_model
from cache.normalize_query import (
    normalize_query
)
def learn_in_background(
        user_input,
        answer):

    try:

        conversation = f"""
User problem:

{user_input}

MemCoder answer:

{answer}
"""

        learned = learn_from_conversation(
            conversation
        )

        # EXPERIENCE
        if "experience" in learned:

            consolidate_and_replace(

                learned["experience"]["task"],

                memory_type="experience",

                execute=True

            )

        # REFLECTIONS
        if "reflections" in learned:

            for reflection in learned["reflections"]:

                consolidate_and_replace(

                reflection,

                memory_type="reflection",

                execute=True
    
             )

        # PRINCIPLES
        if "principles" in learned:

            for principle in learned["principles"]:

                consolidate_and_replace(

                    principle,

                    memory_type="principle",

                    execute=True

                )

        # MISTAKES
        if "mistakes" in learned:

            for mistake in learned["mistakes"]:

                consolidate_and_replace(

                    mistake["task"],

                    memory_type="mistake",

                    execute=True

                )

    except Exception as e:

        print()
        print(
            "Background learning error:",
            e
        )
        print()
def main():

    debug_mode = False
    auto_learn = False

    stats = memory_stats()

    print()
    print("MemCoder v0.1")
    print()
    print("Initializing...")

    get_model()

    print("Ready.")
    print()
    print("Memories  :", stats["total"])
    print("Debug     :", debug_mode)
    print("AutoLearn :", auto_learn)

    print()
    print("Type /exit to quit.")
    print()

    while True:

        user_input = input(
            "MemCoder > "
        )

        # EXIT
        if user_input == "/exit":

            break

        # CLEAR
        if user_input == "/clear":

            clear_history()

            query_cache.clear()

            print()
            print("Session and cache cleared.")
            print()

            continue

        # DEBUG
        if user_input == "/debug":

            debug_mode = not debug_mode

            print()

            if debug_mode:

                print(
                    "Debug mode enabled."
                )

            else:

                print(
                    "Debug mode disabled."
                )

            print()

            continue

        # AUTOLEARN
        if user_input == "/autolearn":

            auto_learn = not auto_learn

            print()

            if auto_learn:

                print(
                    "Auto-learn enabled."
                )

            else:

                print(
                    "Auto-learn disabled."
                )

            print()

            continue

        # STATS
        if user_input == "/stats":

            stats = memory_stats()

            print()

            print(
                "Experiences :",
                stats["experiences"]
            )

            print(
                "Mistakes    :",
                stats["mistakes"]
            )

            print(
                "Principles  :",
                stats["principles"]
            )

            print(
                "Reflections :",
                stats["reflections"]
            )

            print()

            print(
                "Total :",
                stats["total"]
            )

            print()

            continue
        # WHY
        if user_input == "/why":

            show_why()

            continue
        # TRACE
        if user_input == "/trace":

            show_trace()

            continue
        # SEARCH
        if user_input.startswith(
                "/search "):

            query = user_input.replace(
                "/search ",
                ""
            )

            show_search(
                query
            )

            continue
        cache_key = normalize_query(
            user_input
        )
        # CACHE
        if user_input in query_cache:

            print()
            print("(cached answer)")
            print()

            print(
                query_cache[chache_key]["answer"]
            )

            print()

            continue

        # SESSION CONTEXT
        history = get_recent_history()

        session_context = ""

        for turn in history:

            session_context += f"""

User:
{turn["user"]}

Assistant:
{turn["assistant"]}

"""

        print()
        print("Thinking...")
        print()

        start = time.time()

        result = solve_problem(

            user_input,

            session_context=session_context,

            verbose=debug_mode

        )

        elapsed = time.time() - start

        query_cache[cache_key] = result

        print()
        print(result["answer"])
        print()

        print(
            f"Answer time: {elapsed:.2f}s"
        )

        print()

        add_turn(

            user_input,

            result["answer"]

        )

        learn = auto_learn

        if not auto_learn:

            choice = input(
                "Learn this? (y/n): "
            )

            learn = (
                choice.lower() == "y"
            )

        if learn:

            thread = threading.Thread(

                target=learn_in_background,

                args=(
                user_input,
                result["answer"]
                ),

                daemon=True

            )

            thread.start()

    print()
    print("Goodbye.")
    print()


if __name__ == "__main__":

    main()