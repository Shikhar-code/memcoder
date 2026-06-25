from session.session_memory import get_session
from session.task_stack import peek_task
from session.working_memory import get_working_memory
from session.plans import get_plans


def get_agent_state():

    return {

        "session":
            get_session(),

        "current_task":
            peek_task(),

        "working_memory":
            get_working_memory(),

        "plans":
            get_plans()

    }