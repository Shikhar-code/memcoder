from datetime import datetime

def extract_memory(task,
                   files,
                   summary,
                   solution,
                   importance=5,
                   memory_type="experience"):

    memory = {
        "task": task,
        "files": files,
        "summary": summary,
        "solution": solution,
        "importance": importance,
        "type": memory_type,
        "timestamp": str(datetime.now())
    }

    return memory