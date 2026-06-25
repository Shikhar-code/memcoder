from memory.llm_extractor import extract_memory_llm


def extract_domain(raw_text):

    lines = [
        line.strip()
        for line in raw_text.split("\n")
        if line.strip()
    ]

    memories = []

    for line in lines:

        memory = extract_memory_llm(line)

        memories.append(memory)

    return memories