"""
fp_utils.py - Functional Programming Combinators & Utilities.

Provides classic functional constructs:
- Function composition (pipe, compose)
- Currying and partial evaluation
- Immutable tuple transformations (map_tuple, filter_tuple, update_in_tuple)
- Pure mathematical combinators
"""

from functools import reduce, wraps
from typing import Callable, Any, Tuple, TypeVar, Iterable, Optional

T = TypeVar('T')
R = TypeVar('R')


def pipe(value: Any, *functions: Callable[[Any], Any]) -> Any:
    """
    Left-to-right function composition pipeline.
    pipe(x, f, g, h) is equivalent to h(g(f(x))).
    """
    return reduce(lambda acc, f: f(acc), functions, value)


def compose(*functions: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """
    Right-to-left function composition.
    compose(f, g)(x) is equivalent to f(g(x)).
    """
    return lambda initial: reduce(lambda acc, f: f(acc), reversed(functions), initial)


def curry(fn: Callable) -> Callable:
    """
    Converts a function of N arguments into a sequence of functions of 1 argument.
    """
    @wraps(fn)
    def curried(*args, **kwargs):
        if len(args) + len(kwargs) >= fn.__code__.co_argcount:
            return fn(*args, **kwargs)
        return lambda *more_args, **more_kwargs: curried(
            *(args + more_args), **{**kwargs, **more_kwargs}
        )
    return curried


def map_tuple(fn: Callable[[T], R], items: Iterable[T]) -> Tuple[R, ...]:
    """Pure higher-order mapping returning an immutable tuple."""
    return tuple(map(fn, items))


def filter_tuple(predicate: Callable[[T], bool], items: Iterable[T]) -> Tuple[T, ...]:
    """Pure higher-order filtering returning an immutable tuple."""
    return tuple(filter(predicate, items))


def reduce_iterable(fn: Callable[[R, T], R], items: Iterable[T], initial: R) -> R:
    """Pure folding over an iterable."""
    return reduce(fn, items, initial)


def find_first(predicate: Callable[[T], bool], items: Iterable[T], default: Optional[T] = None) -> Optional[T]:
    """Purely find the first item matching predicate, or default."""
    for item in items:
        if predicate(item):
            return item
    return default


def update_in_tuple(items: Tuple[T, ...], predicate: Callable[[T], bool], transform: Callable[[T], T]) -> Tuple[T, ...]:
    """
    Purely updates the item(s) matching predicate in an immutable tuple,
    returning a brand new tuple without mutating the original.
    """
    return tuple(transform(item) if predicate(item) else item for item in items)


def remove_from_tuple(items: Tuple[T, ...], predicate: Callable[[T], bool]) -> Tuple[T, ...]:
    """Purely removes item(s) matching predicate from an immutable tuple."""
    return tuple(item for item in items if not predicate(item))


def clamp(low: float, high: float, val: float) -> float:
    """Clamps a numeric value within [low, high]."""
    return max(low, min(high, val))


def calculate_focus_integrity(active_focus_seconds: int, total_elapsed_seconds: int) -> int:
    """
    Pure mathematical calculation of Focus Integrity percentage (0 to 100).
    Formula: round((active_focus_seconds / total_elapsed_seconds) * 100)
    """
    if total_elapsed_seconds <= 0:
        return 100
    ratio = active_focus_seconds / total_elapsed_seconds
    return int(round(clamp(0.0, 100.0, ratio * 100)))


def format_seconds_to_min_sec(seconds: int) -> str:
    """Pure conversion from integer seconds to MM:SS string."""
    mins = max(0, seconds) // 60
    secs = max(0, seconds) % 60
    return f"{mins:02d}:{secs:02d}"


def calculate_charm_reward(integrity_rate: int, duration_seconds: int, is_strict_mode: bool) -> int:
    """
    Pure functional calculation for Star Charm rewards earned from a focus session.
    High integrity (>=80%) awards maximum charms.
    """
    base_reward = max(1, duration_seconds // 100)  # ~15 coins for 25m
    if integrity_rate >= 90:
        multiplier = 1.3
    elif integrity_rate >= 80:
        multiplier = 1.0
    elif integrity_rate >= 60:
        multiplier = 0.5
    else:
        multiplier = 0.2

    if is_strict_mode:
        multiplier += 0.2

    return max(2, int(round(base_reward * multiplier)))
