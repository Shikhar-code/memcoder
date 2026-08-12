"""Provider-free recording of a solved agent outcome."""

import json

from memory.capture import capture_memory
from memory.principle_capture import capture_principles
from memory.quality import (
    is_valid_experience,
    is_valid_principle,
    is_valid_reflection
)
from memory.reflection_capture import capture_reflection
from memory.records import record_id
from memory.provenance import link


def record_outcome(
        task,
        files,
        summary,
        solution,
        reflection=None,
        principles=None,
        agent_id="human",
        qa_report=None,
        plan_id=None,
        applied_skill_id=None,
        environment=None):
    """Persist only structured memories supplied by the calling agent."""

    recorded = {
        "experience": None,
        "plan_outcome": None,
        "reflections": [],
        "principles": [],
        "rejected": []
    }

    from memory.policy import evaluate_admission
    admission = evaluate_admission(
        files=files,
        text=[task, summary, solution, reflection, *(principles or []), (qa_report or {}).get("evidence")],
        owner=agent_id,
        project_id=(environment or {}).get("project_id") if isinstance(environment, dict) else None,
    )
    if not admission["allowed"]:
        recorded["rejected"].append("policy: " + admission["explanation"])
        return recorded

    if plan_id is not None:
        from memory.plan_outcomes import record_plan_outcome
        recorded["plan_outcome"] = record_plan_outcome(
            plan_id=plan_id,
            task=task,
            qa_report=qa_report,
            agent_id=agent_id,
            applied_skill_id=applied_skill_id,
        )

    if not isinstance(qa_report, dict) or qa_report.get("verdict") != "approved":
        verdict = qa_report.get("verdict") if isinstance(qa_report, dict) else "missing"
        recorded["rejected"].append(
            f"qa: outcome was not admitted (verdict: {verdict})"
        )
        return recorded

    experience = {
        "task": task,
        "files": files,
        "summary": summary,
        "solution": solution
    }

    if is_valid_experience(experience):
        stored_experience = capture_memory(
            task=task,
            files=files,
            summary=summary,
            solution=solution,
            importance=5,
            memory_type="experience",
            owner=agent_id,
            environment=environment,
            verification=json.dumps({
                "qa_schema_version": qa_report.get("schema_version"),
                "qa_verdict": qa_report.get("verdict"),
                "evidence_summary": qa_report.get("evidence_summary", {}),
                "verification_playbook": qa_report.get("verification_playbook", []),
            }, sort_keys=True)
        )

        recorded["experience"] = {
            **experience,
            "id": record_id(stored_experience),
        }
        if recorded["plan_outcome"] is not None:
            link(
                recorded["experience"]["id"],
                recorded["plan_outcome"]["id"],
                "validated_by",
                agent_id,
                metadata={"qa_verdict": qa_report.get("verdict")},
            )
    else:
        recorded["rejected"].append(
            "experience: task, files, summary, and solution must be meaningful"
        )

    if reflection and is_valid_reflection(reflection):
        source_experience_id = (
            recorded["experience"]["id"] if recorded["experience"] else None
        )
        captured_reflection = capture_reflection(
            reflection,
            owner=agent_id,
            source_experience_id=source_experience_id,
            environment=environment,
            verification={
                "qa_schema_version": qa_report.get("schema_version"),
                "qa_verdict": qa_report.get("verdict"),
                "source_experience_id": source_experience_id,
            },
        )

        recorded["reflections"].append({
            "text": reflection,
            "id": record_id(captured_reflection),
            "source_experience_id": source_experience_id,
        })
    elif reflection:
        recorded["rejected"].append(
            "reflection: use one short 'I ...' investigation observation; "
            "do not describe a fix or state a principle"
        )

    valid_principles = [
        principle
        for principle in (principles or [])
        if is_valid_principle(principle)
    ]

    if valid_principles:
        capture_principles(
            valid_principles,
            owner=agent_id,
            source_experience_id=(
                recorded["experience"]["id"] if recorded["experience"] else None
            ),
            environment=environment,
        )

        recorded["principles"] = valid_principles

    invalid_principles = len(principles or []) - len(valid_principles)
    if invalid_principles:
        recorded["rejected"].append(
            f"principles: {invalid_principles} item(s) were not meaningful"
        )

    return recorded
