import unicodedata as ucd
import importlib.resources as rsrc
import json

from .verb import Verb


class Parser:
    """
    Parser for verbs
    """

    def __init__(self):
        """Create instance of a parser and initialize data
        """
        self._ALPHABET = self._load_json("alphabet.json")
        self._SUFFIXES = self._load_json("suffixes.json")
        self._VOWELS = self._load_json("vowels.json")
        self._CONSONANTS = self._load_json("consonants.json")
        self._VOWEL_MAP = {"ee": "i", "ei": "e", "aa": "a", "oo": "u"}

    def _load_json(self, filename: str):
        """
        Read json from a file in the package
        """
        with (
            rsrc.files("tparser.data")
            .joinpath(filename)
            .open("r", encoding="utf-8") as f
        ):
            return json.load(f)

    def _normalize_word(self, word: str) -> str:
        """
        Return a normalized form of the string
        """
        # strip whitespace
        norm = word.strip()

        # replace underlines with the right one
        norm = norm.replace("\u0332", "\u0331")
        print(norm)

        # replace apostrophes with correct one
        norm = norm.replace("\u0027", "\u02bc").replace("\u2019", "\u02bc")
        
        # separate combining accents
        norm = ucd.normalize("NFKD", norm)

        # normalize captialization
        norm = norm.casefold()

        # get rid of other accents
        norm = "".join(
            [c for c in norm if c in self._ALPHABET["chars"]]
        )

        return norm

    def _parse_ending(self, word: Verb, ending_list: list[str]) -> list[Verb]:
        """
        Try to parse given endings from the right of the word
        """
        result = []
        base = word.prefix

        y_variations = ["y", "w", "y\u0308"]

        for ending in ending_list:
            if base.endswith(ending):
                # split it right before the ending
                split_at = len(base) - len(ending)

                # make new word
                new_stem = ending + word.stem
                new_suffix = word.suffix
                new_prefix = base[:split_at]

                parsed = Verb(new_prefix, stem=new_stem, suffix=new_suffix)

                # keep root properties
                parsed.meta["root_form"] = word.meta["root_form"]
                parsed.meta["ablaut"] = word.meta["ablaut"]

                # add to list of possible results if successful
                result.append(parsed)

                # check if ending is one of y/w/umlaut y
                if ending in y_variations:
                    y_variations.remove(ending)
                    y_variation_len = len(ending)

        # if y/w/y umlaut are successfully parsed, then add the other options too
        if len(y_variations) < 3:
            print(base, len(base))
            for y_variation in y_variations:
                print(y_variation, len(y_variation))
                # split it right before the ending
                split_at = len(base) - y_variation_len

                # make new word
                new_stem = y_variation + word.stem
                new_suffix = word.suffix
                new_prefix = base[:split_at]

                parsed = Verb(new_prefix, stem=new_stem, suffix=new_suffix)

                # keep root properties
                parsed.meta["root_form"] = word.meta["root_form"]
                parsed.meta["ablaut"] = word.meta["ablaut"]

                # add to list of possible results if successful
                result.append(parsed)

        return result

    def _parse_suffix(
        self, word: Verb, suffix_list: list[dict[str, str]]
    ) -> list[Verb]:
        """
        Try to parse given suffixes from the right of the word
        """
        result = []
        base = word.prefix

        for suffix in suffix_list:
            if base.endswith(suffix["suffix"]):
                # split it right before the ending
                split_at = len(base) - len(suffix["suffix"])

                # make new word
                new_stem = word.stem
                new_suffix = suffix["suffix"] + word.suffix
                new_prefix = base[:split_at]

                parsed = Verb(new_prefix, stem=new_stem, suffix=new_suffix)
                # indicate in the new word if it's a CV-root suffix
                # or a CVC-root suffix (if it matters for the suffix)
                if suffix["form"] in ("cvc_", "cv_"):
                    parsed.meta["root_form"] = suffix["form"]
                else:
                    parsed.meta["root_form"] = word.meta["root_form"]

                # indicate whether vowel has been changed
                if suffix["ablaut"]:
                    parsed.meta["ablaut"] = True
                else:
                    parsed.meta["ablaut"] = word.meta["ablaut"]

                # add to list of possible results if successful
                result.append(parsed)

        return result

    def _parse_suffixes(self, word: Verb) -> list[Verb]:
        """
        Try to parse all possible suffixes (only one suffix from each type though)
        """
        result_clause = self._parse_suffix(word, self._SUFFIXES["clause"])

        result_tense = self._parse_suffix(word, self._SUFFIXES["tense"])
        for variation in result_clause:
            result_tense.extend(self._parse_suffix(variation, self._SUFFIXES["tense"]))

        result_mod = self._parse_suffix(word, self._SUFFIXES["modality"])
        for variation in result_tense:
            result_mod.extend(self._parse_suffix(variation, self._SUFFIXES["modality"]))

        result_rep = self._parse_suffix(word, self._SUFFIXES["repetitive"])
        for variation in result_mod:
            result_rep.extend(
                self._parse_suffix(variation, self._SUFFIXES["repetitive"])
            )

        result_misc = self._parse_suffix(word, self._SUFFIXES["misc"])
        for variation in result_rep:
            result_misc.extend(self._parse_suffix(variation, self._SUFFIXES["misc"]))

        return result_clause + result_tense + result_mod + result_rep + result_misc

    def _parse_last_consonant(self, word: Verb) -> list[Verb]:
        """
        Try to parse rightmost consonant
        """
        result_mult = self._parse_ending(word, self._CONSONANTS["multiple"])

        # if multi-letter consonant is parsed, return without trying to parse one letter
        if len(result_mult) > 0:
            return result_mult

        # otherwise parse one letter only
        return self._parse_ending(word, self._CONSONANTS["single"])

    def _parse_last_vowel(self, word: Verb) -> list[Verb]:
        """
        Try to parse rightmost vowel
        """
        result_long = self._parse_ending(
            word, self._VOWELS["long_high"] + self._VOWELS["long_low"]
        )

        # if long vowel is parsed, return without trying to parse short vowel
        if len(result_long) > 0:
            return result_long

        # otherwise parse short vowel
        return self._parse_ending(
            word, self._VOWELS["short_high"] + self._VOWELS["short_low"]
        )

    def _parse_last_CVC(self, word: Verb) -> list[Verb]:
        """
        Try to parse a CVC, CVVC syllable from the end of the word
        """
        # try to parse last consonant
        result_last_cons = self._parse_last_consonant(word)
        if not result_last_cons:
            return []

        # try to parse last vowel
        result_vowel = []
        for variation in result_last_cons:
            result_vowel.extend(self._parse_last_vowel(variation))
        result_vowel.extend(self._parse_last_vowel(word))
        if not result_vowel:
            return []

        # try to parse first consonant
        result_syllable = []
        for variation in result_vowel:
            result_syllable.extend(self._parse_last_consonant(variation))

        return result_syllable

    def _parse_last_CV(self, word: Verb) -> list[Verb]:
        """
        Try to parse a CV, CVV syllable from the end of the word
        """
        # try to parse last vowel
        result_vowel = self._parse_last_vowel(word)
        if not result_vowel:
            return []

        # try to parse first consonant
        result_syllable = []
        for variation in result_vowel:
            result_syllable.extend(self._parse_last_consonant(variation))

        return result_syllable

    def _recover_stem(self, word: Verb) -> list[Verb]:
        """
        Try and recover stem changes in the root from parsed verb
        """
        stem = word.stem
        roots = set()

        # remove high tone
        stem = stem.replace("\u0301", "")

        # change all long vowels to short vowels
        for long, short in self._VOWEL_MAP.items():
            stem = stem.replace(long, short)

        # change vowel back to a or u if ablaut
        if word.meta["ablaut"]:
            roots.add(stem.replace("e", "a"))
            roots.add(stem.replace("e", "u"))
        else:
            roots.add(stem)

        results = [Verb(word.prefix, word.stem, word.suffix, r) for r in roots]

        return results

    def parse_word(
        self, word: str, no_display: bool = False
    ) -> list[tuple[str, str, str]]:
        """
        Get possible parsings of a given verb

        params:
            word [str] - the verb, as a string
            no_display [bool] - set to True to suppress output

        returns:
            [list of tuples] - possible parsings in format (prefixes, root, suffixes)
        """
        # make verb object
        normalized = self._normalize_word(word)
        verb = Verb(normalized)

        # try to parse suffixes
        result_suffix = self._parse_suffixes(verb)

        # parse last syllable with suffix
        parsed = []
        if result_suffix:
            for variation in result_suffix:
                # depending on whether suffix attaches to CV or CVC root
                if variation.meta["root_form"] == "cvc":
                    parsed.extend(self._parse_last_CVC(variation))
                elif variation.meta["root_form"] == "cv":
                    parsed.extend(self._parse_last_CV(variation))
                else:
                    parsed.extend(self._parse_last_CVC(variation))
                    parsed.extend(self._parse_last_CV(variation))
        # parse last syllable WITHOUT parsing suffix
        parsed.extend(self._parse_last_CVC(verb))
        parsed.extend(self._parse_last_CV(verb))

        final = []
        for p in parsed:
            final.extend(self._recover_stem(p))

        # convert to friendly representation
        verbs = [p.to_string() for p in final]
        roots = [p.root for p in final]
        result = [p.to_tuple_root() for p in final]

        if not no_display:
            # displaying the possibilities
            print("verb:", verb)
            print("options:", end=" ")
            print(", ".join(verbs))
            print("verb root options:", end=" ")
            print(", ".join(roots))

        return result
