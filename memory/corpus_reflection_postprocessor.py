import re


def postprocess_corpus_reflection(text):

    principles = []

    lines = text.split("\n")

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # remove bullets
        line = re.sub(r"^[-*]\s*", "", line)

        line = line.lower()

        replacements = {

            "regular code reviews and testing":
                "Test continuously.",

            "comprehensive documentation":
                "Maintain clear documentation.",

            "continuous monitoring and alerting systems":
                "Observe systems continuously.",

            "proper error handling and logging practices":
                "Make failures observable.",

            "regular updates and validation of threshold settings":
                "Validate assumptions continuously.",

            "robust reasoning frameworks with well-defined steps":
                "Use structured reasoning.",

            "strict adherence to tool call syntax guidelines":
                "Follow interfaces strictly."
        }

        for key, value in replacements.items():

            if key in line:

                principles.append(value)

    return list(set(principles))