from re import compile, search
from typing import Union


def contains_sub_string(pattern: str, string: str) -> bool:
    pattern = compile(pattern, re.IGNORECASE)

    if search(pattern, string):
        return True

    return False


def calculate_pct_diff(
    data1: Union[float, int], data2: Union[float, int], rounding: int = 2
) -> Union[float, int]:

    if data2 == 0.0:
        raise ZeroDivisionError()

    result = ((data1 - data2) / data2) * 100

    if isinstance(result, float):
        return round(result, rounding)

    return result
