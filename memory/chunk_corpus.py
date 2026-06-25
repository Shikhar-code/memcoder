def chunk_corpus(corpus, chunk_size=10):

    chunks = []

    for i in range(0, len(corpus), chunk_size):

        chunks.append(
            corpus[i:i + chunk_size]
        )

    return chunks