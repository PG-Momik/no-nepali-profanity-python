from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from .lexicon import (
    DEVANAGARI_SUFFIXES,
    LATIN_SUFFIXES,
    LANGUAGES,
    PHRASES,
    STEMS,
    STRICTNESS_LEVELS,
    WORDS,
    LexiconEntry,
)

LANGUAGES_CHECKED: Tuple[str, ...] = LANGUAGES
STRICTNESS_LEVEL: Dict[str, int] = {"lenient": 0, "standard": 1, "strict": 2}

LEET: Dict[str, str] = {
    "0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s",
}

MIN_COLLAPSE = 4

_DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")
_ZERO_WIDTH_RE = re.compile(r"[\u200B-\u200D\u2060\uFEFF]")

_RE_SPECIAL = set(".*+?^${}()|[]\\")
_RE_WILDCARD_SPECIAL = set("*+?^${}()|[]\\")


def is_devanagari(s: str) -> bool:
    return bool(_DEVANAGARI_RE.search(s))


def _is_letter(ch: str) -> bool:
    return ch.isalpha()


def _is_number(ch: str) -> bool:
    return ch.isnumeric()


def _is_letter_or_number(ch: str) -> bool:
    return ch.isalpha() or ch.isnumeric()


def _is_mark(ch: str) -> bool:
    return unicodedata.category(ch)[0] == "M"


def collapse(s: str) -> str:
    """Collapse every run of repeated characters down to one, e.g. "machikneee" -> "machikne"."""
    return re.sub(r"(.)\1+", r"\1", s)


def squeeze(s: str) -> str:
    """Squeeze runs of three or more repeated characters to two, e.g. "mooji" -> "mooji"."""
    return re.sub(r"(.)\1{2,}", r"\1\1", s)


def _normalize_char(ch: str) -> str:
    if _ZERO_WIDTH_RE.fullmatch(ch):
        return ""
    if is_devanagari(ch):
        # Decompose so a precomposed nukta letter loses its nukta, and fold chandrabindu into anusvara.
        decomposed = unicodedata.normalize("NFD", ch)
        decomposed = decomposed.replace("\u093c", "")
        decomposed = decomposed.replace("\u0901", "\u0902")
        return decomposed
    folded = unicodedata.normalize("NFKC", ch).lower()
    return "".join(LEET.get(c, c) for c in folded)


@dataclass
class Normalized:
    text: str
    starts: List[int]
    ends: List[int]


def _normalize(input_text: str) -> Normalized:
    text = ""
    starts: List[int] = []
    ends: List[int] = []
    offset = 0
    for ch in input_text:
        out = _normalize_char(ch)
        text += out
        for _ in range(len(out)):
            starts.append(offset)
            ends.append(offset + len(ch))
        offset += len(ch)

    # Replace each run of "!" between letters or digits with a single "i" spanning the whole run,
    # so a sentence-final "!" stays punctuation.
    result = ""
    result_starts: List[int] = []
    result_ends: List[int] = []
    last = 0
    i = 0
    n = len(text)
    while i < n:
        if text[i] == "!":
            j = i
            while j < n and text[j] == "!":
                j += 1
            before = text[i - 1] if i > 0 else ""
            after = text[j] if j < n else ""
            if before and after and _is_letter_or_number(before) and _is_letter_or_number(after):
                result += text[last:i] + "i"
                result_starts.extend(starts[last:i])
                result_starts.append(starts[i])
                result_ends.extend(ends[last:i])
                result_ends.append(ends[i + (j - i) - 1])
                last = j
                i = j
                continue
        i += 1

    if last == 0:
        return Normalized(text, starts, ends)
    result += text[last:]
    result_starts.extend(starts[last:])
    result_ends.extend(ends[last:])
    return Normalized(result, result_starts, result_ends)


def normalize_text(s: str) -> str:
    return _normalize(s).text


def _escape_regex(s: str) -> str:
    return "".join("\\" + c if c in _RE_SPECIAL else c for c in s)


def _wildcard_regex(s: str) -> re.Pattern:
    parts = []
    for c in s:
        if c == "*":
            parts.append(".")
        elif c in _RE_WILDCARD_SPECIAL:
            parts.append("\\" + c)
        else:
            parts.append(c)
    return re.compile("^" + "".join(parts) + "$", re.IGNORECASE)


@dataclass
class Tables:
    latin_exact: set
    latin_collapsed: set
    latin_words: List[str]
    latin_stems: List[str]
    dev_words: set
    dev_stems: List[str]
    phrases: List[str]
    phrase_patterns: List[re.Pattern]


def _active(entries: Tuple[LexiconEntry, ...], devanagari: bool, languages: set, level: int) -> List[str]:
    out = []
    for e in entries:
        if e.language in languages and STRICTNESS_LEVEL[e.strictness] <= level:
            if (e.language == "devanagari") == devanagari:
                out.append(normalize_text(e.text))
    return out


def _phrase_whitespace_regex(phrase: str) -> re.Pattern:
    body = "\\s+".join(_escape_regex(w) for w in phrase.strip().split())
    return re.compile(body)


def build_tables(options: Optional[Dict] = None) -> Tables:
    options = options or {}
    languages = set(options.get("languages", LANGUAGES_CHECKED))
    for l in languages:
        if l not in LANGUAGES_CHECKED:
            raise TypeError(f'Unknown language "{l}". Use one of: {", ".join(LANGUAGES_CHECKED)}.')
    strictness = options.get("strictness", "standard")
    level = STRICTNESS_LEVEL.get(strictness)
    if level is None:
        raise TypeError(f'Unknown strictness "{strictness}". Use one of: {", ".join(STRICTNESS_LEVELS)}.')

    latin_words = _active(WORDS, False, languages, level)
    latin_stems = [collapse(s) for s in _active(STEMS, False, languages, level)]

    phrases = [*_active(PHRASES, False, languages, level), *_active(PHRASES, True, languages, level)]

    return Tables(
        latin_exact=set(squeeze(w) for w in latin_words),
        latin_collapsed=set(collapse(w) for w in latin_words if len(collapse(w)) >= MIN_COLLAPSE),
        latin_words=[squeeze(w) for w in latin_words],
        latin_stems=latin_stems,
        dev_words=set(_active(WORDS, True, languages, level)),
        dev_stems=_active(STEMS, True, languages, level),
        phrases=phrases,
        phrase_patterns=[_phrase_whitespace_regex(p) for p in phrases],
    )


def _wildcard_token_matches(tables: Tables, token: str) -> bool:
    if "*" not in token:
        return False

    clean_token = token.strip("*")
    if not any(_is_letter(c) for c in clean_token):
        return False

    # "*" on both ends is markdown emphasis ("*sh*t*"). On one end only, it may also hide a first or last letter ("*ss").
    emphasis = token.startswith("*") and token.endswith("*")
    tokens = [clean_token] if emphasis or clean_token == token else [clean_token, token]
    forms = [form for t in tokens for form in (squeeze(t), collapse(t))]

    for f in forms:
        regex = _wildcard_regex(f)
        if any(regex.fullmatch(w) for w in tables.latin_words):
            return True
        for stem in tables.latin_stems:
            if len(f) < len(stem):
                continue
            if _wildcard_regex(f[: len(stem)]).fullmatch(stem):
                return True
    return False


def _latin_token_matches(tables: Tables, token: str) -> bool:
    candidates = [token]
    for s in LATIN_SUFFIXES:
        if token.endswith(s) and len(token) - len(s) >= 3:
            candidates.append(token[: -len(s)])
            break

    for t in candidates:
        squeezed = squeeze(t)
        collapsed = collapse(t)
        if (
            squeezed in tables.latin_exact
            or (len(collapsed) >= MIN_COLLAPSE and collapsed in tables.latin_collapsed)
            or any(collapsed.startswith(stem) for stem in tables.latin_stems)
            or _wildcard_token_matches(tables, t)
        ):
            return True
    return False


def _devanagari_token_matches(tables: Tables, token: str) -> bool:
    candidates = [token]
    for s in DEVANAGARI_SUFFIXES:
        if token.endswith(s) and len(token) > len(s) + 1:
            candidates.append(token[: -len(s)])
            break

    return any(t in tables.dev_words or any(t.startswith(stem) for stem in tables.dev_stems) for t in candidates)


@dataclass
class Span:
    value: str
    start: int
    end: int


def _token_spans(n: Normalized) -> List[Span]:
    tokens: List[Span] = []
    run: List[Span] = []

    # Three or more single letters in a row ("f.u.c.k", "f u c k") are read as one word.
    def flush() -> None:
        if len(run) >= 3:
            tokens.append(
                Span(
                    value="".join(t.value for t in run),
                    start=run[0].start,
                    end=run[-1].end,
                )
            )
        run.clear()

    text = n.text
    i = 0
    while i < len(text):
        ch = text[i]
        if _is_letter(ch) or _is_mark(ch) or ch == "*":
            j = i
            while j < len(text) and (_is_letter(text[j]) or _is_mark(text[j]) or text[j] == "*"):
                j += 1
            t = Span(value=text[i:j], start=n.starts[i], end=n.ends[j - 1])
            if is_devanagari(t.value):
                flush()
                tokens.append(t)
            elif len(t.value) == 1:
                run.append(t)
            else:
                flush()
                tokens.append(t)
            i = j
        else:
            i += 1
    flush()
    return tokens


def tokenize(text: str) -> List[str]:
    """The raw tokens the matcher sees. Useful for debugging why a word is (or isn't) caught."""
    if not text:
        return []
    return [t.value for t in _token_spans(_normalize(text))]


@dataclass
class ProfanityMatch:
    """One place where profanity was found in the original text."""

    text: str
    normalized: str
    start: int
    end: int


def _scan(tables: Tables, text: str) -> List[ProfanityMatch]:
    if not text:
        return []

    n = _normalize(text)

    def make(normalized: str, start: int, end: int) -> ProfanityMatch:
        return ProfanityMatch(text=text[start:end], normalized=normalized, start=start, end=end)

    found: List[ProfanityMatch] = []

    for t in _token_spans(n):
        matches = (
            _devanagari_token_matches(tables, t.value)
            if is_devanagari(t.value)
            else _latin_token_matches(tables, t.value)
        )
        if matches:
            found.append(make(t.value, t.start, t.end))

    for index, re_pattern in enumerate(tables.phrase_patterns):
        for m in re_pattern.finditer(n.text):
            start, end = m.start(), m.end()
            word_start_ok = start == 0 or not _is_letter_or_number(n.text[start - 1])
            word_end_ok = end >= len(n.text) or not _is_letter_or_number(n.text[end])
            if word_start_ok and word_end_ok:
                found.append(make(n.text[start:end], n.starts[start], n.ends[end - 1]))

    return found


def _unique(matches: List[ProfanityMatch]) -> List[str]:
    return list(dict.fromkeys(m.normalized for m in matches))


def _by_position(matches: List[ProfanityMatch]) -> List[ProfanityMatch]:
    return sorted(matches, key=lambda m: (m.start, -m.end))


_INDIC_VIRAMAS = frozenset(
    "\u094d\u09cd\u0a4d\u0acd\u0b4d\u0bcd\u0c4d\u0ccd\u0d4d\u0dca"
)


def _graphemes(s: str) -> List[str]:
    clusters: List[str] = []
    for ch in s:
        if clusters and (_is_grapheme_extend(ch) or (ch.isalpha() and _ends_with_virama(clusters[-1]))):
            clusters[-1] += ch
            continue
        clusters.append(ch)
    return clusters


def _ends_with_virama(cluster: str) -> bool:
    """Whether a consonant joins this cluster: it ends in a virama, perhaps followed by other marks or a ZWJ."""
    for c in reversed(cluster):
        if c in _INDIC_VIRAMAS:
            return True
        if c != "\u200d" and unicodedata.category(c) != "Mn":
            return False
    return False


def _is_grapheme_extend(ch: str) -> bool:
    category = unicodedata.category(ch)
    return (
        category in ("Mn", "Mc", "Me")
        or "\ufe00" <= ch <= "\ufe0f"
        or ch in "\u200c\u200d"
    )


@dataclass
class ProfanityCheck:
    """The result of scanning one text: inspect it, then censor it without scanning again."""

    text: str
    has_profanity: bool
    words: List[str]
    matches: List[ProfanityMatch]
    _raw_matches: List[ProfanityMatch] = field(default_factory=list, repr=False)

    def censor(self, options: Optional[Dict] = None) -> str:
        return _censor_matches(self.text, self._raw_matches or self.matches, options)


def _censor_matches(text: str, matches: List[ProfanityMatch], options: Optional[Dict] = None) -> str:
    options = options or {}
    mask = options.get("mask", "*")
    replace = options.get("replace")
    if not isinstance(mask, str) or mask == "":
        raise TypeError("mask must be a non-empty string.")
    if replace is not None and not callable(replace):
        raise TypeError("replace must be callable.")

    # Merge overlapping matches, such as the word "chaak" inside the phrase "chaak ko pwal", into one.
    merged: List[ProfanityMatch] = []
    for m in _by_position(matches):
        prev = merged[-1] if merged else None
        if prev is not None and m.start < prev.end:
            if m.end > prev.end:
                prev.end = m.end
                prev.text = text[prev.start : prev.end]
        else:
            merged.append(ProfanityMatch(text=m.text, normalized=m.normalized, start=m.start, end=m.end))

    out = ""
    last = 0
    for m in merged:
        if replace is not None:
            replacement = replace(m)
        else:
            pieces = []
            for g in _graphemes(m.text):
                pieces.append(mask if not _is_whitespace(g) else g)
            replacement = "".join(pieces)
        out += text[last : m.start] + replacement
        last = m.end
    return out + text[last:]


def _is_whitespace(s: str) -> bool:
    return all(c.isspace() for c in s)


class ProfanityFilter:
    """Builds a filter once for a set of options. Reuse it rather than passing options on every call."""

    def __init__(self, options: Optional[Dict] = None) -> None:
        self._tables = build_tables(options)

    def check(self, text: str) -> ProfanityCheck:
        matches = _scan(self._tables, text)
        return ProfanityCheck(
            text=text,
            has_profanity=bool(matches),
            words=_unique(matches),
            matches=_by_position(matches),
            _raw_matches=matches,
        )

    def contains_profanity(self, text: str) -> bool:
        return bool(_scan(self._tables, text))

    def find_profanity(self, text: str) -> List[str]:
        return _unique(_scan(self._tables, text))

    def find_profanity_matches(self, text: str) -> List[ProfanityMatch]:
        return _by_position(_scan(self._tables, text))

    def censor(self, text: str, options: Optional[Dict] = None) -> str:
        return _censor_matches(text, _scan(self._tables, text), options)


def create_filter(options: Optional[Dict] = None) -> ProfanityFilter:
    return ProfanityFilter(options)


_filter_cache: Dict[tuple, ProfanityFilter] = {}


def _cached_filter(options: Optional[Dict] = None) -> ProfanityFilter:
    options = options or {}
    key = (
        options.get("strictness", ""),
        tuple(sorted(options.get("languages", LANGUAGES_CHECKED))),
    )
    _filter = _filter_cache.get(key)
    if _filter is None:
        _filter = create_filter(options)
        _filter_cache[key] = _filter
    return _filter


def check(text: str, options: Optional[Dict] = None) -> ProfanityCheck:
    """Scans the text once. Use the result to check for profanity and to censor it, e.g. check(text).censor()."""
    return _cached_filter(options).check(text)


def contains_profanity(text: str, options: Optional[Dict] = None) -> bool:
    """Yes/no from find_profanity."""
    return _cached_filter(options).contains_profanity(text)


def find_profanity(text: str, options: Optional[Dict] = None) -> List[str]:
    """Matching words, normalised and lowercased, deduplicated. Empty when clean."""
    return _cached_filter(options).find_profanity(text)


def find_profanity_matches(text: str, options: Optional[Dict] = None) -> List[ProfanityMatch]:
    """Every occurrence with its position in the original text, sorted by position."""
    return _cached_filter(options).find_profanity_matches(text)


def censor(text: str, options: Optional[Dict] = None) -> str:
    """The text with each match masked, e.g. "you muji" -> "you ****"."""
    options = options or {}
    mask = options.get("mask", "*")
    replace = options.get("replace")
    filter_options = {k: v for k, v in options.items() if k not in ("mask", "replace")}
    return _cached_filter(filter_options).censor(text, {"mask": mask, "replace": replace})