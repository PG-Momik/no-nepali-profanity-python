from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from .lexicon import (
    ALLOWED,
    DEVANAGARI_SUFFIXES,
    INFIXES,
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
    "0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "8": "b", "9": "g", "@": "a", "$": "s", "€": "e",
}

# Cyrillic and Greek letters that look like Latin ones, so "fuсk" with a Cyrillic с still reads as "fuck".
CONFUSABLES: Dict[str, str] = {
    "а": "a", "в": "b", "е": "e", "ё": "e", "к": "k", "м": "m", "н": "h", "о": "o", "р": "p", "с": "c", "т": "t",
    "у": "y", "х": "x", "ѕ": "s", "і": "i", "ї": "i", "ј": "j", "ԁ": "d", "α": "a", "β": "b", "ε": "e", "ι": "i",
    "κ": "k", "ν": "v", "ο": "o", "ρ": "p", "τ": "t", "υ": "u", "χ": "x",
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


def romanize(s: str) -> str:
    """Fold the spellings of छ, chh and x, into x.

    Romanized entries and tokens are both folded before they're compared, so xakka matches chhakka. It also keeps
    छ apart from च once letters are collapsed, so chhod ("leave") no longer matches the stem chod.
    """
    return squeeze(s).replace("chh", "x")


def _normalize_char(ch: str) -> str:
    if _ZERO_WIDTH_RE.fullmatch(ch):
        return ""
    if is_devanagari(ch):
        # Decompose so a precomposed nukta letter loses its nukta, and fold chandrabindu into anusvara.
        decomposed = unicodedata.normalize("NFD", ch)
        decomposed = decomposed.replace("\u093c", "")
        decomposed = decomposed.replace("\u0901", "\u0902")
        return decomposed
    # Accents are removed, so "fück" reads as "fuck".
    folded = unicodedata.normalize("NFD", unicodedata.normalize("NFKC", ch).lower())
    return "".join(LEET.get(c, CONFUSABLES.get(c, c)) for c in folded if not _is_mark(c))


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
    latin_stems: List[str]
    roman_exact: set
    roman_collapsed: set
    roman_stems: List[str]
    # Every Latin word and stem, unfolded, for wildcard tokens.
    wild_words: List[str]
    wild_stems: List[str]
    infixes: List[str]
    # The infixes with no doubled letter, which are also looked for in the collapsed token.
    plain_infixes: List[str]
    allowed: set
    dev_words: set
    dev_stems: List[str]
    dev_allowed: set
    phrases: List[str]
    phrase_patterns: List[re.Pattern]


def _active(entries: Tuple[LexiconEntry, ...], language: str, languages: set, level: int) -> List[str]:
    if language not in languages:
        return []
    return [
        normalize_text(e.text)
        for e in entries
        if e.language == language and STRICTNESS_LEVEL[e.strictness] <= level
    ]


def _string_list(value, name: str) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str) or not all(isinstance(w, str) for w in value):
        raise TypeError(f"{name} must be a list of strings.")
    return [w.strip() for w in value if w.strip()]


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

    extra_words = [normalize_text(w) for w in _string_list(options.get("extra_words"), "extra_words")]
    allow_words = [normalize_text(w) for w in [*ALLOWED, *_string_list(options.get("allow_words"), "allow_words")]]

    # Extra words count as English: matched as they are, without the Romanized spelling folds.
    english_words = [*_active(WORDS, "english", languages, level), *(w for w in extra_words if not is_devanagari(w))]
    roman_words_raw = _active(WORDS, "romanized", languages, level)
    roman_words = [romanize(w) for w in roman_words_raw]
    english_stems = _active(STEMS, "english", languages, level)
    roman_stems = _active(STEMS, "romanized", languages, level)
    infixes = [squeeze(i) for i in _active(INFIXES, "english", languages, level)]

    phrases = [p for lang in LANGUAGES_CHECKED for p in _active(PHRASES, lang, languages, level)]

    return Tables(
        latin_exact=set(squeeze(w) for w in english_words),
        latin_collapsed=set(collapse(w) for w in english_words if len(collapse(w)) >= MIN_COLLAPSE),
        latin_stems=[collapse(s) for s in english_stems],
        roman_exact=set(roman_words),
        roman_collapsed=set(collapse(w) for w in roman_words if len(collapse(w)) >= MIN_COLLAPSE),
        roman_stems=[collapse(romanize(s)) for s in roman_stems],
        wild_words=[squeeze(w) for w in [*english_words, *roman_words_raw]],
        wild_stems=[collapse(s) for s in [*english_stems, *roman_stems]],
        infixes=infixes,
        plain_infixes=[i for i in infixes if collapse(i) == i],
        allowed=set(squeeze(w) for w in allow_words if not is_devanagari(w)),
        dev_words=set([*_active(WORDS, "devanagari", languages, level), *(w for w in extra_words if is_devanagari(w))]),
        dev_stems=_active(STEMS, "devanagari", languages, level),
        dev_allowed=set(w for w in allow_words if is_devanagari(w)),
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
        if any(regex.fullmatch(w) for w in tables.wild_words):
            return True
        for stem in tables.wild_stems:
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

    if any(squeeze(t) in tables.allowed for t in candidates):
        return False

    for t in candidates:
        squeezed = squeeze(t)
        collapsed = collapse(t)
        roman = romanize(t)
        roman_collapsed = collapse(roman)
        if (
            squeezed in tables.latin_exact
            or (len(collapsed) >= MIN_COLLAPSE and collapsed in tables.latin_collapsed)
            or any(collapsed.startswith(stem) for stem in tables.latin_stems)
            or roman in tables.roman_exact
            or (len(roman_collapsed) >= MIN_COLLAPSE and roman_collapsed in tables.roman_collapsed)
            or any(roman_collapsed.startswith(stem) for stem in tables.roman_stems)
            or any(i in squeezed for i in tables.infixes)
            or any(i in collapsed for i in tables.plain_infixes)
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

    if any(t in tables.dev_allowed for t in candidates):
        return False
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


# Characters that can split a word without a space: "sh.it", "fu-ck", "b_i_tch".
_GLUE_RE = re.compile(r"[._\-~'`]+")
MAX_GLUED_PIECES = 6
MAX_GLUED_LENGTH = 12


def _is_token_char(ch: str) -> bool:
    return _is_letter(ch) or _is_mark(ch) or ch == "*"


def _glued_spans(n: Normalized) -> List[Span]:
    """Runs of Latin letters split only by glue characters, read as one word.

    A run is joined only if one of its pieces is three letters or fewer and the joined word is at most 12 letters,
    so "shital.shrestha" in an email address stays two words.
    """
    text = n.text
    runs: List[Tuple[str, int, int]] = []
    i = 0
    while i < len(text):
        if _is_token_char(text[i]):
            j = i
            while j < len(text) and _is_token_char(text[j]):
                j += 1
            if not is_devanagari(text[i:j]):
                runs.append((text[i:j], i, j))
            i = j
        else:
            i += 1

    spans: List[Span] = []
    group: List[Tuple[str, int, int]] = []

    def flush() -> None:
        length = sum(len(r[0]) for r in group)
        if (
            2 <= len(group) <= MAX_GLUED_PIECES
            and length <= MAX_GLUED_LENGTH
            and any(len(r[0]) <= 3 for r in group)
        ):
            spans.append(Span("".join(r[0] for r in group), n.starts[group[0][1]], n.ends[group[-1][2] - 1]))
        group.clear()

    for r in runs:
        if group and not _GLUE_RE.fullmatch(text[group[-1][2] : r[1]]):
            flush()
        group.append(r)
    flush()
    return spans


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

    # A glued word is only read joined when none of its pieces matched on its own.
    for g in _glued_spans(n):
        if any(m.start < g.end and g.start < m.end for m in found):
            continue
        if _latin_token_matches(tables, g.value):
            found.append(make(g.value, g.start, g.end))

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
        tuple(options.get("extra_words") or ()),
        tuple(options.get("allow_words") or ()),
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