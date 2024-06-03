# Copyright (c) 2021 The Toltec Contributors
# SPDX-License-Identifier: MIT
"""Collection of useful functions."""

import itertools
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Protocol,
    Sequence,
    TypeVar,
)


# See <https://github.com/python/typing/issues/760>
class SupportsLessThan(Protocol):  # pylint:disable=too-few-public-methods
    """Types that support the less-than operator."""

    def __lt__(self, other: Any) -> bool:
        ...


Key = TypeVar("Key", bound=SupportsLessThan)
Value = TypeVar("Value")


def group_by(
    in_seq: Sequence[Value], key_fn: Callable[[Value], Key]
) -> Dict[Key, List[Value]]:
    """
    Group elements of a list.

    :param in_seq: list of elements to group
    :param key_fn: mapping of each element onto a group
    :returns: dictionary of groups
    """
    return dict(
        (key, list(group))
        for key, group in itertools.groupby(
            sorted(in_seq, key=key_fn), key=key_fn
        )
    )
