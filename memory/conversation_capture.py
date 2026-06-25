from memory.llm_extractor import extract_memory_llm
from memory.capture import capture_memory
from memory.postprocessor import postprocess_memory
from memory.importance import score_importance

def capture_conversation(conversation):

    memory = extract_memory_llm(conversation)

    memory = postprocess_memory(memory)

    memory["importance"] = score_importance(memory)

    return capture_memory(
        memory["task"],
        memory["files"],
        memory["summary"],
        memory["solution"],
    )