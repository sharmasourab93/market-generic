from re import compile, search


def contains_sub_string(pattern: str, string: str) -> bool:
    pattern = compile(pattern, re.IGNORECASE)

    if search(pattern, string):
        return True

    return False
