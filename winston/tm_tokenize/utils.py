from typing import List
from typing import Match
from typing import TypeVar


T = TypeVar("T")


def uniquely_constructed(t: T) -> T:
    """avoid tuple.__hash__ for "singleton" constructed objects"""
    t.__hash__ = object.__hash__  # type: ignore
    return t
