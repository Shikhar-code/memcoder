from api.memcoder_api import (
    solve,
    learn
)


class MemCoderSession:

    def __init__(
            self,
            agent):

        self.agent = agent

        self.history = []

    def solve(
            self,
            query):

        session_context = self.context()

        result = solve(

            query,

            session_context=session_context,

            agent_id=self.agent.id

        )

        self.history.append(

            {

                "user": query,

                "assistant": result["answer"]

            }

        )

        return result

    def learn(self):

        conversation = self.context()

        return learn(

            conversation,

            agent_id=self.agent.id

        )

    def context(self):

        text = ""

        for turn in self.history:

            text += f"""

User:

{turn['user']}

Assistant:

{turn['assistant']}

"""

        return text

    def clear(self):

        self.history = []

    def __repr__(self):

        return f"MemCoderSession(agent={self.agent.id}, turns={len(self.history)})"

    __str__ = __repr__