"""A small, dependency-free profanity matcher for English, Romanized (Latin) Nepali and Devanagari Nepali."""

from .core import (
    ProfanityCheck,
    ProfanityFilter,
    ProfanityMatch,
    censor,
    check,
    contains_profanity,
    create_filter,
    find_profanity,
    find_profanity_matches,
    tokenize,
)
from . import lexicon

__version__ = "0.1.0"

__all__ = [
    "ProfanityCheck",
    "ProfanityFilter",
    "ProfanityMatch",
    "censor",
    "check",
    "contains_profanity",
    "create_filter",
    "find_profanity_matches",
    "find_profanity",
    "lexicon",
    "tokenize",
    "__version__",
]