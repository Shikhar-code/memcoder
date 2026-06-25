def build_hierarchical_context(results):

    context = ""

    # EXPERIENCES
    if results["experiences"]:

        context += "\nPAST EXPERIENCES\n\n"

        for memory in results["experiences"]:

            context += f"""
Problem:
{memory["task"]}

Fix:
{memory["solution"]}

---
"""

    # MISTAKES
    if results["mistakes"]:

        context += "\nAVOID\n\n"

        for memory in results["mistakes"]:

            context += f"""
{memory["summary"]}

Fix:
{memory["solution"]}

---
"""

    # PRINCIPLES
    if results["principles"]:

        context += "\nRULES\n\n"

        for memory in results["principles"]:

            context += f"""
{memory["summary"]}

---
"""

    # REFLECTIONS
    if results["reflections"]:

        context += "\nOBSERVATIONS\n\n"

        for memory in results["reflections"]:

            context += f"""
{memory["summary"]}

---
"""

    return context