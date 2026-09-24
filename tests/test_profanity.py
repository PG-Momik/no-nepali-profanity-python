import pytest
from dataclasses import asdict

from no_nepali_profanity import (
    censor,
    check,
    contains_profanity,
    create_filter,
    find_profanity,
    find_profanity_matches,
    tokenize,
)


class TestContainsProfanity:
    @pytest.mark.parametrize(
        ("label", "text"),
        [
            ("English", "what a bitch"),
            ("an inflected English word (stem)", "fucking useless"),
            ("Romanized Nepali", "muji teacher"),
            ("Romanized Nepali with a postposition", "machikneko class"),
            ("Devanagari Nepali", "यो मुजी हो"),
            ("Devanagari with a postposition", "मुजीको कक्षा"),
            ("Devanagari with a nukta or zero-width joiner", "मु\u200dजी"),
            ("leetspeak", "sh1t lecturer"),
            ("leetspeak with @", "@ss"),
            ("leetspeak with $", "a$$"),
            ("dodging with ! for i inside a word", "sh!t lecturer"),
            ("dodging with a wildcard for a hidden letter", "f*ck this"),
            ("dodging with a wildcard for the hidden i", "sh*t"),
            ("markdown emphasis still reads the word", "*sh*t* is bad"),
            ("stretched letters", "fuuuuck"),
            ("letters spelled out with dots", "f.u.c.k"),
            ("letters spelled out with spaces", "m u j i"),
            ("upper case", "IDIOT"),
            ("Hindi slang common in Nepal", "chutiya"),
            ("Romanized invective", "murkha"),
            ("Dodged word stays caught with a suffix", "gandako budi"),
            ("exact word, not a long place name", "look at that gand"),
            ("stem catches the -ne inflected form", "chodne manche"),
            ("Devanagari invective", "मुर्ख"),
            ("Devanagari slang", "कमिना"),
            ("Devanagari vulgar term", "लुंड"),
            ("multi-word phrase", "chaak ko pwal"),
            ("multi-word phrase with leetspeak", "p3sa g@rne taba"),
            ("multi-word phrase ending a sentence", "thulo sasto manche!"),
            ("review-supplied term", "chhakka lai hami mukhulla bhanchha"),
            ("short spelling from words.csv", "mji"),
            ("leet spelling from words.csv", "m00ji"),
            ("English leet spelling from words.csv", "f4ck off"),
            ("Devanagari spelling from words.csv", "राण्डी"),
            ("Latin phrase from words.csv", "khatako choro"),
            ("Devanagari phrase from words.csv", "राण्डीको बान"),
            ("spelling variant with -ey", "yo khatey payment app kahiley chaley po"),
        ],
    )
    def test_catches(self, label, text):
        assert contains_profanity(text) is True

    @pytest.mark.xfail(
        reason=(
            "Wildcard for a hidden first letter (\"that *ss\") isn't caught — ported as-is from the npm package; "
            "see the upstream README's Known issues."
        )
    )
    def test_wildcard_for_hidden_first_letter(self):
        assert contains_profanity("that *ss") is True

    @pytest.mark.parametrize(
        "text",
        [
            "The class assignment was as hard as expected",
            "Computing and data structures",
            "Dickson explained Scunthorpe problems",
            "Assam and Gandaki are places",
            "Kshitij Shrestha",
            "Shitij Adhikari",
            "Putali Gurung",
            "पुतली गुरुङ",
            "Randip Thapa",
            "Asha Sharma",
            "Machindra Karki",
            "Harimaya Tamang",
            "सीता कार्की",
            "क्षितिज श्रेष्ठ",
            "Great teacher!",
            "No way! That can't be right",
            "the starred items are on page 12*",
            "feed ** me ** the list",
            "chicken biryani is good",
            "the salaam greeting sounded nice",
            "Gandaki river is in Nepal",
            "sasto ra manche duitai ho",
            "terms and conditions",
            "the conductor",
            "bhrastachar kanda",
            "Kandel sir",
            "Lundberg",
            "fohor pani",
            "kano manche",
            "lato keta",
            "फोहोर पानी",
            "लाटो केटा",
        ],
    )
    def test_does_not_flag(self, text):
        assert find_profanity(text) == []

    def test_is_false_for_empty_string(self):
        assert contains_profanity("") is False


class TestTokenize:
    def test_joins_spelled_out_letters_and_keeps_devanagari_whole(self):
        assert tokenize("f.u.c.k this") == ["fuck", "this"]
        assert tokenize("सीता कार्की") == ["सीता", "कार्की"]

    def test_keeps_wildcard_and_sentence_final_bang(self):
        assert tokenize("f*ck this!") == ["f*ck", "this"]


class TestLanguagesOption:
    def test_checks_only_enabled_languages(self):
        romanized = {"languages": ["romanized"]}
        assert contains_profanity("muji", romanized) is True
        assert contains_profanity("fuck", romanized) is False
        assert contains_profanity("मुजी", romanized) is False
        assert contains_profanity("sasto manche", romanized) is True

    def test_keeps_languages_separate(self):
        assert find_profanity("fuck muji मुजी", {"languages": ["english"]}) == ["fuck"]
        assert find_profanity("fuck muji मुजी", {"languages": ["devanagari"]}) == ["मुजी"]

    def test_checks_nothing_when_no_language_is_on(self):
        assert find_profanity("fuck muji मुजी", {"languages": []}) == []

    def test_rejects_an_unknown_language(self):
        with pytest.raises(TypeError):
            create_filter({"languages": ["hindi"]})


class TestStrictnessOption:
    def test_lenient_skips_milder_insults(self):
        assert contains_profanity("idiot", {"strictness": "lenient"}) is False
        assert contains_profanity("murkha", {"strictness": "lenient"}) is False
        assert contains_profanity("sasto manche", {"strictness": "lenient"}) is False
        assert contains_profanity("muji", {"strictness": "lenient"}) is True

    def test_standard_is_the_default(self):
        assert contains_profanity("idiot") is True
        assert contains_profanity("idiot", {"strictness": "standard"}) is True
        assert contains_profanity("Randip Thapa") is False

    def test_strict_adds_stems_that_hit_ordinary_words(self):
        strict = {"strictness": "strict"}
        assert find_profanity("randikoban", strict) == ["randikoban"]
        assert find_profanity("terms and conditions", strict) == ["conditions"]
        assert find_profanity("Randip Thapa", strict) == ["randip"]

    def test_rejects_an_unknown_strictness(self):
        with pytest.raises(TypeError):
            create_filter({"strictness": "max"})


class TestCreateFilter:
    def test_combines_both_options(self):
        filter = create_filter({"languages": ["romanized"], "strictness": "lenient"})
        assert filter.contains_profanity("muji") is True
        assert filter.contains_profanity("murkha") is False
        assert filter.find_profanity("fuck muji") == ["muji"]


class TestFindProfanityMatches:
    def test_returns_every_occurrence_with_position(self):
        assert [asdict(m) for m in find_profanity_matches("F.U.C.K this sh1t, muji. MUJI")] == [
            {"text": "F.U.C.K", "normalized": "fuck", "start": 0, "end": 7},
            {"text": "sh1t", "normalized": "shit", "start": 13, "end": 17},
            {"text": "muji", "normalized": "muji", "start": 19, "end": 23},
            {"text": "MUJI", "normalized": "muji", "start": 25, "end": 29},
        ]

    def test_returns_a_phrase_before_a_word_it_contains(self):
        assert [asdict(m) for m in find_profanity_matches("chaak ko pwal")] == [
            {"text": "chaak ko pwal", "normalized": "chaak ko pwal", "start": 0, "end": 13},
            {"text": "chaak", "normalized": "chaak", "start": 0, "end": 5},
        ]

    def test_is_empty_for_clean_text(self):
        assert find_profanity_matches("Great teacher!") == []
        assert find_profanity_matches("") == []


class TestCensor:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("you muji", "you ****"),
            ("F.U.C.K this Sh1t!", "******* this ****!"),
            ("sh!!t happens", "***** happens"),
            ("ＦＵＣＫ off", "**** off"),
            ("fuuuuck yeah", "******* yeah"),
            ("f*ck and *sh*t*", "**** and ******"),
            ("muji muji", "**** ****"),
            ("you 😀 muji 😀", "you 😀 **** 😀"),
        ],
    )
    def test_masks(self, text, expected):
        assert censor(text) == expected

    def test_masks_devanagari_by_visible_character(self):
        assert censor("मुजीको कक्षा") == "*** कक्षा"

    def test_keeps_spaces_inside_a_phrase(self):
        assert censor("sasto   manche") == "*****   ******"

    def test_merges_a_word_with_the_phrase_around_it(self):
        assert censor("chaak ko pwal") == "***** ** ****"

    def test_leaves_clean_text_and_names_alone(self):
        assert censor("Great teacher!") == "Great teacher!"
        assert censor("Shitij is great") == "Shitij is great"
        assert censor("") == ""

    def test_uses_a_custom_mask_character(self):
        assert censor("you muji", {"mask": "#"}) == "you ####"

    def test_uses_a_replace_function_over_the_mask(self):
        assert censor("you muji fuck", {"mask": "#", "replace": lambda m: "[censored]"}) == (
            "you [censored] [censored]"
        )
        assert censor("you muji", {"replace": lambda m: m.text[0] + "*" * (len(m.text) - 1)}) == "you m***"

    def test_respects_the_filter_options(self):
        assert censor("fuck muji", {"languages": ["romanized"]}) == "fuck ****"
        assert censor("you idiot", {"strictness": "lenient"}) == "you idiot"
        assert create_filter({"strictness": "strict"}).censor("Randip Thapa") == "****** Thapa"

    def test_rejects_an_empty_mask(self):
        with pytest.raises(TypeError):
            censor("muji", {"mask": ""})


class TestCheck:
    def test_returns_everything_from_one_scan(self):
        result = check("you muji, F.U.C.K")
        assert result.text == "you muji, F.U.C.K"
        assert result.has_profanity is True
        assert result.words == ["muji", "fuck"]
        assert [m.text for m in result.matches] == ["muji", "F.U.C.K"]
        assert result.censor() == "you ****, *******"
        assert result.censor({"mask": "#"}) == "you ####, #######"

    def test_chains_straight_into_censor(self):
        assert check("you muji").censor() == "you ****"
        assert check("Great teacher!").censor() == "Great teacher!"

    def test_reports_clean_text(self):
        result = check("Great teacher!")
        assert result.has_profanity is False
        assert result.words == []
        assert result.matches == []

    def test_respects_the_filter_options(self):
        assert check("fuck muji", {"languages": ["romanized"]}).censor() == "fuck ****"
        assert create_filter({"strictness": "lenient"}).check("you idiot").has_profanity is False