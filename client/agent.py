from client.session import MemCoderSession

from api.memcoder_api import (
    solve,
    learn,
    search,
    trace,
    stats,
    delete,
    update,
    share,
    transfer,
    clear
)


class MemCoderAgent:

    def __init__(self, agent_id):

        self.id = agent_id

    # -----------------------
    # Factory constructors
    # -----------------------

    @classmethod
    def coder(cls):
        return cls("coder")

    @classmethod
    def research(cls):
        return cls("research")

    @classmethod
    def planner(cls):
        return cls("planner")

    @classmethod
    def human(cls):
        return cls("human")

    # -----------------------
    # Sessions
    # -----------------------

    def session(self):

        return MemCoderSession(
            self
        )

    # -----------------------
    # Learning
    # -----------------------

    def learn(
            self,
            conversation):

        return learn(

            conversation,

            agent_id=self.id

        )

    # -----------------------
    # Solving
    # -----------------------

    def solve(
            self,
            query,
            session_context=""):

        return solve(

            query,

            session_context=session_context,

            agent_id=self.id

        )

    # -----------------------
    # Search
    # -----------------------

    def search(
            self,
            query,
            k=3,
            memory_type=None):

        return search(

            query,

            k=k,

            memory_type=memory_type,

            agent_id=self.id

        )

    def search_one(
            self,
            query,
            memory_type=None):

        results = self.search(

            query,

            k=1,

            memory_type=memory_type

        )

        if len(results) == 0:

            return None

        return results[0]

    def exists(
            self,
            query,
            memory_type=None):

        return self.search_one(

            query,

            memory_type

        ) is not None

    # -----------------------
    # Memory Management
    # -----------------------

    def update(
            self,
            memory_id,
            **updates):

        return update(

            memory_id,

            **updates

        )

    def delete(
            self,
            memory_id):

        return delete(
            memory_id
        )

    def share(
            self,
            memory_id):

        return share(
            memory_id
        )

    def transfer(
            self,
            memory_id,
            owner):

        return transfer(

            memory_id,

            owner

        )

    def clear(self):

        return clear(
            self.id
        )

    # -----------------------
    # Retrieval
    # -----------------------

    def trace(
            self,
            query):

        return trace(

            query,

            agent_id=self.id

        )

    # -----------------------
    # Stats
    # -----------------------

    def stats(self):

        return stats()

    # -----------------------
    # Python niceties
    # -----------------------

    def __repr__(self):

        return f"MemCoderAgent({self.id})"

    __str__ = __repr__