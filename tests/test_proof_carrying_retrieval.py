"""Retrieved guidance must include evidence, limits, risks, and verification."""

import json

from memory.proof import build_proof


memory = {
    "record_state": "trusted",
    "applicability": "changed",
    "environment": json.dumps({"project_id": "education-pipeline", "fingerprint": "old"}),
    "verification": json.dumps({"qa_verdict": "approved"}),
    "provenance": [
        {
            "relation": "supports",
            "source_id": "experience-1",
            "target_id": "skill-1",
            "direction": "incoming",
        },
        {
            "relation": "contradicts",
            "source_id": "newer-record",
            "target_id": "skill-1",
            "direction": "incoming",
        },
    ],
    "skill_definition": json.dumps({
        "verification": ["Run the focused production QA check."],
    }),
}

proof = build_proof(memory)
assert proof["record_state"] == "trusted"
assert proof["applicability"] == "changed"
assert {item["relation"] for item in proof["evidence"]} == {
    "supports", "contradicts", "qa_verdict"
}
assert proof["conditions"][0] == "Applies to project: education-pipeline."
assert proof["required_verification"] == ["Run the focused production QA check."]
assert any("fingerprint changed" in risk for risk in proof["risks"])
assert any("contradicts" in risk for risk in proof["risks"])
assert "verify: Run the focused production QA check." in proof["summary"]

print("PASS: proof-carrying retrieval contract")
