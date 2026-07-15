from fastapi import FastAPI

from api.memcoder_api import (
    solve,
    learn,
    search,
    trace,
    stats
)

from server.models import (
    SolveRequest,
    LearnRequest,
    SearchRequest,
    TraceRequest
)

app = FastAPI(
    title="MemCoder API",
    description="Memory infrastructure for humans and agents",
    version="0.1"
)


@app.get("/")
def root():

    return {

        "message": "MemCoder API"

    }


@app.post("/solve")
def solve_endpoint(
        request: SolveRequest):

    return solve(

        request.query,

        request.session_context,

        request.agent_id

    )


@app.post("/learn")
def learn_endpoint(
        request: LearnRequest):

    learn(

        request.conversation,

        agent_id=request.agent_id

    )

    return {

        "status": "success"

    }


@app.post("/search")
def search_endpoint(
        request: SearchRequest):

    return search(

        request.query,

        k=request.k,

        memory_type=request.memory_type,

        agent_id=request.agent_id

    )


@app.post("/trace")
def trace_endpoint(
        request: TraceRequest):

    return trace(

        request.query,

        agent_id=request.agent_id

    )


@app.get("/stats")
def stats_endpoint():

    return stats()
