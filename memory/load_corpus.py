from memory.load_raw import load_raw


def load_corpus():

    domains = [
        "remotion",
        "ml",
        "web",
        "database",
        "systems",
        "windows",
        "research",
        "devops",
        "ai",
        "general"
    ]

    corpus = []

    for domain in domains:

        memories = load_raw(domain)

        corpus.extend(memories)

    return corpus