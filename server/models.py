from pydantic import BaseModel


class SolveRequest(BaseModel):

    query: str

    session_context: str = ""

    agent_id: str = "human"


class LearnRequest(BaseModel):

    conversation: str

    agent_id: str = "human"


class SearchRequest(BaseModel):

    query: str

    k: int = 3

    memory_type: str | None = None

    agent_id: str = "human"


class TraceRequest(BaseModel):

    query: str

    agent_id: str = "human"