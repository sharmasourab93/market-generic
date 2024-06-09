from re import compile, search
from typing import Union, List
from functools import lru_cache, wraps
from time import monotonic_ns


def timed_lru_cache(seconds: int = 60, max_size: int = 128, typed: bool = False):
    def wrapper_cache(f):
        f = lru_cache(maxsize=max_size, typed=typed)(f)
        f.delta = seconds * 10**9
        f.expiration = monotonic_ns() + f.delta

        @wraps(f)
        def wrapper_f(*args, **kwargs):
            if monotonic_ns() >= f.expiration:
                f.cache_clear()
                f.expiration = monotonic_ns() + f.delta

            return f(*args, **kwargs)

        wrapper_f.cache_info = f.cache_info
        wrapper_f.cache_clear = f.cache_clear
        return wrapper_f
    return wrapper_cache


def find_least_difference_strike(strikes: List[int]):

    min_diff = float("inf")

    for i in range(len(strikes) -1):
        diff = abs(strikes[i] - strikes[i+1])

        if diff < min_diff:
            min_diff = diff

    return min_diff


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
