chat_history = []


def add_turn(
        user,
        assistant):

    chat_history.append(

        {
            "user": user,
            "assistant": assistant
        }

    )


def get_recent_history(
        n=5):

    return chat_history[-n:]


def clear_history():

    chat_history.clear()