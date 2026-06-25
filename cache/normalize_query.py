import re


def normalize_query(query):

    query = query.strip()

    query = query.lower()

    query = query.rstrip(".")

    query = query.rstrip("?")

    query = re.sub(
        r"\s+",
        " ",
        query
    )

    return query