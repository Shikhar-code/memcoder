from datetime import datetime

def extract_memory(task,
                   files,
                   summary,
                   solution,
                   importance=5,
                   memory_type="experience",
                   source=None,
                   verification=None):

    memory = {
        "task": task,
        "files": files,
        "summary": summary,
        "solution": solution,
        "importance": importance,
        "type": memory_type,
        "timestamp": str(datetime.now())
    }

    if source:
        memory["source"] = source

    if verification:
        memory["verification"] = verification

    return memory
