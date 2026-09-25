# no-nepali-profanity

A small, **dependency-free** profanity matcher for **English**, **Romanized (Latin) Nepali** and **Devanagari Nepali**,
plus the Hindi slang common in Nepal. Built for moderating user-written text — names, comments, reviews — on Nepali
sites, where false positives on real names are more damaging than a missed swear.

Zero runtime dependencies. Python ≥ 3.9. A direct port of the
[no-nepali-profanity](https://github.com/PG-Momik/no-nepali-profanity) npm package, with the same word lists and
matching rules.

**Documentation: [mukhxadnahunna.com/python](https://mukhxadnahunna.com/python/)**

## Install

```sh
pip install no-nepali-profanity
```

## Usage

```py
from no_nepali_profanity import contains_profanity, find_profanity, tokenize

# boolean check — fastest
contains_profanity("Great teacher!")        # False
contains_profanity("muji")                  # True
contains_profanity("मुजीको कक्षा")           # True  (Devanagari + postposition)

# which words — returns normalised matches as they appeared
find_profanity("f.u.c.k this sh1t")        # ["fuck", "shit"]
find_profanity("f u c k this")              # ["fuck"]
find_profanity("Randip Thapa")              # []
find_profanity("*ss teacher")               # ["*ss"]

# debugging — see what the matcher actually splits into
tokenize("Great teacher!")                  # ["great", "teacher"]
```

## API

| Function | Returns | Notes |
|---|---|---|
| `contains_profanity(text, options?)` | `bool` | Yes/no from `find_profanity`. |
| `find_profanity(text, options?)` | `list[str]` | Matching words **normalised + lowercased** (leet decoded, case-folded), deduplicated. Empty when clean. |
| `check(text, options?)` | `ProfanityCheck` | Scans once; inspect the result and censor it without scanning again. |
| `find_profanity_matches(text, options?)` | `list[ProfanityMatch]` | Every occurrence with its position in the original text, sorted by position. |
| `censor(text, options?)` | `str` | The text with each match masked: `"you muji"` → `"you ****"`. Options: `mask` (default `"*"`), `replace(match)`. |
| `create_filter(options?)` | `ProfanityFilter` | Builds the tables once for fixed options. |
| `tokenize(text)` | `list[str]` | Raw tokens the matcher sees. Useful for debugging why a word is (or isn't) caught. |
| `lexicon` | module | Tagged entries (`WORDS`, `STEMS`, `PHRASES`), flat per-script lists (`LATIN_WORDS`, `DEVANAGARI_WORDS`…) and suffixes. |

Match positions (`ProfanityMatch.start`, `end`) are character (code point) indices, unlike the npm package which
uses UTF-16 code units.

### Censoring

```py
censor("you muji")                                   # "you ****"
censor("F.U.C.K this Sh1t!")                          # "******* this ****!"
censor("you muji", {"mask": "#"})                     # "you ####"
censor("you muji", {"replace": lambda m: "[censored]"})  # "you [censored]"
find_profanity_matches("you muji")                     # [ProfanityMatch(text="muji", normalized="muji", start=4, end=8)]
```

Check and censor in one pass:

```py
result = check("you muji")
result.has_profanity   # True
result.words           # ["muji"]
result.censor()        # "you ****"
```

### Options

```py
find_profanity("fuck muji मुजी", {"languages": ["romanized"]})      # ["muji"]
contains_profanity("you idiot", {"strictness": "lenient"})         # False
find_profanity("terms and conditions", {"strictness": "strict"})   # ["conditions"]
```

- `languages`: any of `"english"`, `"romanized"`, `"devanagari"`. Default: all three.
- `strictness`: `"lenient"` (severe words only), `"standard"` (default, adds milder insults like `idiot`, `murkha`) or
  `"strict"` (adds the stems `rand`, `cond`, `kand`, `lund`, which also hit words like `Randip` and `conditions`).

## What it catches

- **Case and Unicode forms**: `IDIOT`, full-width letters.
- **Leetspeak**: `sh1t`, `@ss` (`0 1 3 4 5 7 @ $`).
- **`!` for `i` between letters**: `sh!t`, `b!tch`. Sentence-final `Great teacher!` is left alone.
- **`*` for a hidden letter**: `f*ck`, `sh*t`, and markdown emphasis like `*sh*t*` still reads as the word.
- **Stretched letters**: `fuuuuck`, for words of 4+ letters.
- **Spelled-out letters**: `f.u.c.k`, `f u c k`.
- **Nepali postpositions and plurals glued on**: `mujiko`, `randiharu`, `मुजीको`, `…हरू`.
- **Devanagari spelling variants**: nukta, chandrabindu vs anusvara, zero-width joiners.
- **Stems** where no ordinary word starts the same way: `fucking`, `bitches`, `machiknee`.
- **Multi-word phrases**: `chaak ko pwal`, `pesa garne`, `sasto manche` (Latin and Devanagari).

## What it deliberately doesn't

- **Short words match exactly**, so `as`, `class`, `assignment` and `Assam` are fine.
- **Name collisions**: `shit` is a whole word only, because **Shitij / शितिज** is a name. Names like **मुजी**-adjacent
  **Randip / राण्डीप**, **Putali / पुतली**, **Asha / आशा** are checked in the test suite.
- **No caste names, surnames or ordinary words that are only offensive in context** (e.g. *kami*, *kukur*). A word
  list can't tell a slur from someone's name; that needs human moderation.
- **No judgement of context, sarcasm or meaning.** This is a first-pass filter, not a moderator.

## Development

```sh
python -m venv .venv && .venv/bin/pip install -e ".[test]"
.venv/bin/pytest
```

The word lists live in `src/no_nepali_profanity/lexicon.py`, apart from the matching logic in
`src/no_nepali_profanity/core.py`. Native-speaker review of the Nepali lists is the most valuable contribution.

## License

MIT