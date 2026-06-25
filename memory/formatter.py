def format_results(results):

    output = ""

    for i, memory in enumerate(results, start=1):

        output += (
            f"{i}. {memory['task']}\n"
            f"   Files: {', '.join(memory['files'])}\n"
            f"   Solution: {memory['solution']}\n"
            f"   Distance: {memory['score']:.4f}\n\n"
        )

    return output