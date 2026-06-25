def build_problem_description(task):

    description = f"""
Current problem:

{task}

You are retrieving memories for a coding assistant.

Prefer memories with:

1. Same framework.
2. Same failure mode.
3. Same files.
4. Same technology stack.
5. Same domain.

Examples:

Remotion render crashes should prefer:

- WebGL problems
- video rendering problems
- React rendering problems
- composition issues
- memory issues during rendering

Avoid:

- kernel crashes
- operating system bugs
- networking issues
- unrelated APIs

Return memories that would help solve the problem.
"""

    return description