from memory.clear import clear_owner

from agent.problem_solver import solve_problem

from memory.conversation_learner import (
    learn_from_conversation
)

from memory.search import search_memory

from memory.stats import memory_stats

from memory.hierarchical_search import (
    hierarchical_search
)
from memory.delete import delete_memory
from memory.update import update_memory
from memory.share import share_memory
from memory.transfer import transfer_memory
def solve(
        query,
        session_context="",
        agent_id="human"):

    return solve_problem(
        query,
        session_context=session_context,
        agent_id=agent_id
    )


def learn(
        conversation,
        agent_id="human"):

    return learn_from_conversation(
        conversation,
        agent_id=agent_id
    )


def search(
        query,
        k=3,
        memory_type=None,
        agent_id="human"):

    return search_memory(
        query=query,
        k=k,
        memory_type=memory_type,
        agent_id=agent_id
    )
def share(
        memory_id):

    return share_memory(
        memory_id
    )


def transfer(
        memory_id,
        owner):

    return transfer_memory(
        memory_id,
        owner
    )

def delete(
        memory_id):

    return delete_memory(
        memory_id
    )
def update(
        memory_id,
        **updates):

    return update_memory(

        memory_id,

        **updates

    )

def clear(
        owner):

    return clear_owner(
        owner
    )

def stats():

    return memory_stats()


def trace(
        query,
        agent_id="human"):

    return hierarchical_search(
        query,
        agent_id=agent_id
    )