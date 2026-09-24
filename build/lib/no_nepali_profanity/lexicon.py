from __future__ import annotations

from typing import NamedTuple, Tuple

Language = str
Strictness = str

LANGUAGES: Tuple[str, ...] = ("english", "romanized", "devanagari")
STRICTNESS_LEVELS: Tuple[str, ...] = ("lenient", "standard", "strict")


class LexiconEntry(NamedTuple):
    text: str
    language: Language
    strictness: Strictness


def _tag(language: Language, strictness: Strictness, texts: Tuple[str, ...]) -> Tuple[LexiconEntry, ...]:
    return tuple(LexiconEntry(text=text, language=language, strictness=strictness) for text in texts)


WORDS: Tuple[LexiconEntry, ...] = (
    *_tag("english", "lenient", (
        "fuck", "fuk", "fck", "phuck", "shit", "shitty", "shithead", "bullshit", "bitch", "bastard", "ass",
        "asshole", "arsehole", "dumbass", "dick", "dickhead", "cunt", "whore", "slut", "cock", "pussy", "twat",
        "wanker", "retard", "fack",
    )),
    *_tag("english", "standard", ("piss", "idiot", "stupid", "moron")),

    *_tag("romanized", "lenient", (
        "muji", "mujhi", "muzi", "machikne", "machhikne", "mchikne", "mcikne", "machikney", "randi", "raandi",
        "rando", "rande", "radi", "lado", "lodo", "puti", "geda", "jatha", "jantha", "jathya", "chikne", "chikney",
        "bhalu", "khate", "khatey", "harami", "gandu", "chutiya", "chutia", "bhosdi", "bhosadi", "bhosdike", "bsdk",
        "madarchod", "behenchod", "bhenchod", "chhakka", "lauro", "gukhane", "gand", "gaand", "gandako", "lund",
        "lundra", "lundri", "chod", "chodna", "beshya", "hijada", "kamina", "haramzada", "turi", "pakhe", "condo",
        "kando", "chaak", "gula", "bajiya", "mji", "mzi", "mujj", "mooji", "moozi", "mcne", "mechikne", "laado",
        "puuti", "zatya", "chodeko", "toori", "kundo",
    )),
    *_tag("romanized", "standard", (
        "kutta", "kutti", "kuttiya", "murkha", "badmas", "sala", "saley", "sali", "chhucho", "chhuchi", "gu",
        "thukk", "nalayak", "beijjat", "nikamma", "ghinlagdo", "nindaniya", "paji", "moot", "bhate", "chhura",
        "torpe", "mukhulla", "gobre", "bhusya", "dhurt",
    )),

    *_tag("devanagari", "lenient", (
        "मुजी", "मुजि", "माचिक्ने", "मचिक्ने", "रण्डी", "रन्डी", "रंडी", "रांडी", "रण्डो", "राण्डे", "राडी", "लाडो",
        "लांडो", "पुती", "गेडा", "जाठा", "जांठा", "जाठ्या", "चिक्ने", "भालु", "खाते", "हरामी", "गान्डु", "गांडु",
        "चुतिया", "भोस्डी", "भोसडी", "भोस्डीके", "मादरचोद", "बहनचोद", "भेनचोद", "छक्का", "लौरो", "गुखाने", "गान्ड",
        "गाण्ड", "गान्डको", "लुंड", "लुण्ड", "लुन्ड्रा", "लुन्ड्री", "लोडो", "चोद", "चोद्ना", "चोदेको", "वेश्या",
        "हिजडा", "कमिना", "हरामजादा", "तुरी", "पाखे", "कोंडो", "काण्डो", "कुन्डो", "चाक", "गुला", "बजिया",
        "राण्डी", "गाण्डु", "भोसडीके", "गाण्डको", "कोन्डो",
    )),
    *_tag("devanagari", "standard", (
        "कुत्ता", "कुत्ती", "कुत्तिया", "मुर्ख", "मूर्ख", "बदमास", "साला", "साले", "साली", "छुच्चो", "छुच्ची", "गु",
        "किचकिच", "थुक", "नालायक", "बेइज्जत", "निकम्मा", "घिनलाग्दो", "निन्दनीय", "पाजी", "मूत", "भाते", "छुरा",
        "टोर्पे", "मुखुल्ला", "गोबरे", "भुस्या", "धूर्त",
    )),
)

STEMS: Tuple[LexiconEntry, ...] = (
    *_tag("english", "lenient", (
        "fuck", "motherfuck", "bitch", "bastard", "asshol", "cunt", "whore", "slut", "wank", "retard",
    )),
    *_tag("romanized", "lenient", (
        "machikn", "mchikn", "chutiy", "bhosd", "madarch", "behench", "bhench", "chikn", "chickn", "chod", "jath",
    )),
    *_tag("romanized", "strict", ("rand", "cond", "kand", "lund")),
    *_tag("devanagari", "lenient", (
        "माचिक्न", "मचिक्न", "चुतिय", "भोस्ड", "मादरच", "बहनच", "भेनच", "चोद", "चिक्न", "रण्ड", "लुण्ड", "जाठ",
    )),
    *_tag("devanagari", "strict", ("कोन्ड", "कान्ड")),
)

PHRASES: Tuple[LexiconEntry, ...] = (
    *_tag("romanized", "lenient", (
        "chaak ko pwal", "tero aama ko", "muji jasto", "lado khaye", "lado khos", "randi ko choro", "randi ko ban",
        "gand mara", "gand fatchya", "geda jasto", "geda khaya", "khatako choro", "bhaluko ban", "machikne khate",
    )),
    *_tag("romanized", "standard", ("pesa garne", "sasto manche")),
    *_tag("devanagari", "lenient", (
        "चाकको प्वाल", "चाक को प्वाल", "तेरो आमाको", "मुजी जस्तो", "लाडो खाए", "लाडो खोस्", "राण्डीको छोरो",
        "राण्डीको बान", "गाण्ड मरा", "गाण्ड फाट्या", "गेडा जस्तो", "गेडा खाया", "खातेको छोरो", "भालुको बान",
        "माचिक्ने खाते",
    )),
    *_tag("devanagari", "standard", ("पेसा गर्ने", "सस्तो मान्छे")),
)

LATIN_SUFFIXES: Tuple[str, ...] = (
    "haruko", "harule", "haru", "sanga", "bata", "lai", "ko", "ki", "ka", "le", "ma", "ni", "ne", "yo",
)

DEVANAGARI_SUFFIXES: Tuple[str, ...] = (
    "हरूको", "हरुको", "हरूले", "हरुले", "हरू", "हरु", "बाट", "सँग", "संग", "लाई", "को", "की", "का", "ले",
    "मा", "नि", "ने", "यो",
)


def _texts(entries: Tuple[LexiconEntry, ...], latin: bool) -> Tuple[str, ...]:
    return tuple(e.text for e in entries if (e.language != "devanagari") == latin)


LATIN_WORDS: Tuple[str, ...] = _texts(WORDS, True)
LATIN_STEMS: Tuple[str, ...] = _texts(STEMS, True)
LATIN_PHRASES: Tuple[str, ...] = _texts(PHRASES, True)
DEVANAGARI_WORDS: Tuple[str, ...] = _texts(WORDS, False)
DEVANAGARI_STEMS: Tuple[str, ...] = _texts(STEMS, False)
DEVANAGARI_PHRASES: Tuple[str, ...] = _texts(PHRASES, False)

__all__ = [
    "DEVANAGARI_PHRASES",
    "DEVANAGARI_STEMS",
    "DEVANAGARI_SUFFIXES",
    "DEVANAGARI_WORDS",
    "LATIN_PHRASES",
    "LATIN_STEMS",
    "LATIN_SUFFIXES",
    "LATIN_WORDS",
    "LANGUAGES",
    "LexiconEntry",
    "PHRASES",
    "STEMS",
    "STRICTNESS_LEVELS",
    "WORDS",
]