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
        "fag", "fags", "faggot", "faggots", "fagot", "faggy", "nigger", "niggers", "nigga", "niggas", "tranny",
        "kike", "shitface", "shithole", "dipshit", "horseshit", "batshit", "apeshit", "jackass", "asshat", "asswipe",
        "cocksucker", "jizz", "dildo", "skank", "douchebag", "motherfucker", "bollocks", "bellend",
    )),
    *_tag("english", "standard", (
        "piss", "idiot", "stupid", "moron",
        "crap", "crappy", "bugger", "douche", "jerk", "scumbag", "dumb", "wtf", "stfu", "tits", "boobs", "porn",
        "porno", "horny", "bimbo", "thot",
    )),

    # Each of these is also an ordinary word: spic (span), chink (in the armour), dyke (a wall), hoe (a tool), cum
    # (laude), prick (a pin), damn.
    *_tag("english", "strict", (
        "spic", "chink", "dyke", "hoe", "cum", "prick", "damn", "rape",
    )),
    *_tag("romanized", "lenient", (
        "muji", "mujhi", "muzi", "machikne", "machhikne", "mchikne", "mcikne", "machikney", "randi", "raandi",
        "rando", "rande", "radi", "lado", "lodo", "puti", "geda", "jatha", "jantha", "jathya", "chikne", "chikney",
        "bhalu", "khate", "khatey", "harami", "gandu", "chutiya", "chutia", "bhosdi", "bhosadi", "bhosdike", "bsdk",
        "madarchod", "behenchod", "bhenchod", "chhakka", "lauro", "gukhane", "gand", "gaand", "gandako", "lund",
        "lundra", "lundri", "chod", "chodna", "beshya", "hijada", "kamina", "haramzada", "turi", "pakhe", "condo",
        "kando", "chaak", "gula", "bajiya", "mji", "mzi", "mujj", "mooji", "moozi", "mcne", "mechikne", "laado",
        "puuti", "zatya", "chodeko", "toori", "kundo",
        "chhakke", "maxikne", "mxikne", "xutiya", "xutia", "chhutiya", "chootiya", "xikne", "jhant", "jhaant",
        "jhantu", "lauda", "lavda", "lawda", "loda", "lwado", "lwada", "bhosda", "bhosri", "chhinal", "chhinar",
        "besya", "maachod", "madarchood",
    )),
    *_tag("romanized", "standard", (
        "kutta", "kutti", "kuttiya", "murkha", "badmas", "sala", "saley", "sali", "chhucho", "chhuchi", "gu",
        "thukk", "nalayak", "beijjat", "nikamma", "ghinlagdo", "nindaniya", "paji", "moot", "bhate", "chhura",
        "torpe", "mukhulla", "gobre", "bhusya", "dhurt",
        "gadha", "ullu", "badmash", "thukka", "haramkhor", "fataha",
    )),

    *_tag("devanagari", "lenient", (
        "मुजी", "मुजि", "माचिक्ने", "मचिक्ने", "रण्डी", "रन्डी", "रंडी", "रांडी", "रण्डो", "राण्डे", "राडी", "लाडो",
        "लांडो", "पुती", "गेडा", "जाठा", "जांठा", "जाठ्या", "चिक्ने", "भालु", "खाते", "हरामी", "गान्डु", "गांडु",
        "चुतिया", "भोस्डी", "भोसडी", "भोस्डीके", "मादरचोद", "बहनचोद", "भेनचोद", "छक्का", "लौरो", "गुखाने", "गान्ड",
        "गाण्ड", "गान्डको", "लुंड", "लुण्ड", "लुन्ड्रा", "लुन्ड्री", "लोडो", "चोद", "चोद्ना", "चोदेको", "वेश्या",
        "हिजडा", "कमिना", "हरामजादा", "तुरी", "पाखे", "कोंडो", "काण्डो", "कुन्डो", "चाक", "गुला", "बजिया",
        "राण्डी", "गाण्डु", "भोसडीके", "गाण्डको", "कोन्डो",
        "छिनाल", "झांट", "झाँट", "लौडा", "लवडा",
    )),
    *_tag("devanagari", "standard", (
        "कुत्ता", "कुत्ती", "कुत्तिया", "मुर्ख", "मूर्ख", "बदमास", "साला", "साले", "साली", "छुच्चो", "छुच्ची", "गु",
        "किचकिच", "थुक", "थुक्क", "नालायक", "बेइज्जत", "निकम्मा", "घिनलाग्दो", "निन्दनीय", "पाजी", "मूत", "भाते", "छुरा",
        "टोर्पे", "मुखुल्ला", "गोबरे", "भुस्या", "धूर्त",
        "गधा", "उल्लु", "उल्लू", "बदमाश", "थुक्का", "हरामखोर", "फटाहा",
    )),
)

STEMS: Tuple[LexiconEntry, ...] = (
    *_tag("english", "lenient", (
        "fuck", "motherfuck", "bitch", "bastard", "asshol", "cunt", "whore", "slut", "wank", "retard",
        "shit", "nigger", "cocksuck", "bullshit", "dickhead", "douchebag", "jizz", "dildo",
    )),
    *_tag("romanized", "lenient", (
        "machikn", "mchikn", "chutiy", "bhosd", "madarch", "behench", "bhench", "chikn", "chickn", "chod", "jath",
        "xutiy", "chhutiy", "maxikn", "jhant",
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
        "teri maa ki", "teri ma ki",
    )),
    *_tag("romanized", "standard", (
        "pesa garne", "sasto manche",
        "gu khane", "gu khaa",
    )),
    *_tag("devanagari", "lenient", (
        "चाकको प्वाल", "चाक को प्वाल", "तेरो आमाको", "मुजी जस्तो", "लाडो खाए", "लाडो खोस्", "राण्डीको छोरो",
        "राण्डीको बान", "गाण्ड मरा", "गाण्ड फाट्या", "गेडा जस्तो", "गेडा खाया", "खातेको छोरो", "भालुको बान",
        "माचिक्ने खाते",
    )),
    *_tag("devanagari", "standard", ("पेसा गर्ने", "सस्तो मान्छे")),
)

# Latin roots caught anywhere inside a word, not just at its start: dumbfuck, sonofabitch. Only roots that no ordinary
# word contains are here; the few that do, like Scunthorpe, are in ALLOWED.
INFIXES: Tuple[LexiconEntry, ...] = (
    *_tag("english", "lenient", (
        "fuck", "cunt", "bitch", "whore", "nigger", "faggot", "jizz",
    )),
)

# Ordinary words and names that a stem or an embedded root would otherwise flag. A word here is never flagged, with or
# without a postposition (Randipko, Shitijlai), at any strictness.
ALLOWED: Tuple[str, ...] = (
    "shitij", "shitiz", "shital", "shitala", "shitalpati", "shitanshu", "shiitake", "shitake", "shiite", "shiites",
    "shiitic", "niger", "nigeria", "nigerian", "nigerians", "nigerien", "snigger", "sniggers", "sniggered",
    "sniggering", "sniggerer", "scunthorpe", "randip", "randeep", "randhir", "randhawa", "random", "randomly",
    "randomness", "randomize", "randomized", "randy", "condition", "conditions", "conditional", "conditionally",
    "conditioner", "conditioning", "conditioned", "conduct", "conducts", "conducted", "conducting", "conductor",
    "conductors", "conduction", "conductive", "condense", "condensed", "condenser", "condemn", "condemned",
    "condolence", "condolences", "condiment", "kanda", "kandel", "kandu", "kandahar", "lundberg", "lundup",
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
LATIN_INFIXES: Tuple[str, ...] = _texts(INFIXES, True)
DEVANAGARI_WORDS: Tuple[str, ...] = _texts(WORDS, False)
DEVANAGARI_STEMS: Tuple[str, ...] = _texts(STEMS, False)
DEVANAGARI_PHRASES: Tuple[str, ...] = _texts(PHRASES, False)

__all__ = [
    "ALLOWED",
    "DEVANAGARI_PHRASES",
    "DEVANAGARI_STEMS",
    "DEVANAGARI_SUFFIXES",
    "DEVANAGARI_WORDS",
    "INFIXES",
    "LATIN_INFIXES",
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