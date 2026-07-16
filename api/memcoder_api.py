from memory.clear import clear_owner

from memory.search import search_memory

from memory.stats import memory_stats

from memory.hierarchical_search import (
    hierarchical_search
)
from memory.delete import delete_memory
from memory.update import update_memory
from memory.share import share_memory
from memory.transfer import transfer_memory
from memory.record_outcome import record_outcome
from memory.markdown_import import (
    import_markdown as import_markdown_memory,
    import_markdown_file as import_markdown_file_memory
)


def solve(
        query,
        session_context="",
        agent_id="human"):

    from agent.solve_and_learn import solve_and_learn

    return solve_and_learn(
        query,
        session_context=session_context,
        agent_id=agent_id
    )


def learn(
        conversation,
        agent_id="human"):

    from memory.conversation_learner import learn_from_conversation

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
        agent_id="human",
        include_shared=True):

    return hierarchical_search(
        query,
        agent_id=agent_id,
        include_shared=include_shared
    )


def prepare(
        query,
        agent_id="human",
        include_shared=True):

    return hierarchical_search(
        query,
        agent_id=agent_id,
        include_shared=include_shared
    )


def record(
        task,
        files,
        summary,
        solution,
        reflection=None,
        principles=None,
        agent_id="human"):

    return record_outcome(
        task=task,
        files=files,
        summary=summary,
        solution=solution,
        reflection=reflection,
        principles=principles,
        agent_id=agent_id
    )


def import_markdown(
        markdown,
        source_name,
        agent_id="human",
        approve=False):
    return import_markdown_memory(
        markdown=markdown,
        source_name=source_name,
        agent_id=agent_id,
        approve=approve
    )


def import_markdown_file(
        file_path,
        agent_id="human",
        approve=False):
    return import_markdown_file_memory(
        file_path=file_path,
        agent_id=agent_id,
        approve=approve
    )
