"""Minimal provider-free SDK example."""

from memcoder import intervene_cognition


packet = intervene_cognition(
    "Validate a required request field before processing it.",
    agent_id="demo-project",
    include_shared=False,
)

print(packet["intervention"])
print(packet["guidance"]["recommended_next_action"])
