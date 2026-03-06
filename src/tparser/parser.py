import pandas as pd
import unicodedata as ucd
import importlib.resources as rsrc
import json

from verb import Verb

class Parser:
    """
    Parser for verbs
    """

    _PREFIX = 0
    _STEM = 1
    _SUFFIX = 2

    def __init__(self):
        # initialize data
        self._ALPHABET = self._load_json("alphabet.json")
        self._SUFFIXES = self._load_json("suffixes.json")
        self._VOWELS = self._load_json("vowels.json")
        self._CONSONANTS = self._load_json("consonants.json")


    def _load_json(self, filename: str):
        '''
        Read json from a file in the package
        '''
        with rsrc.files("tparser.data").joinpath(filename).open("r", encoding="utf-8") as f:
            return json.load(f)
        

    def _normalize_word(self, word: str) -> str:
        '''
        Return a normalized form of the string
        '''
        # strip whitespace
        norm_whitesp = word.strip()

        # separate combining accents
        norm_combining = ucd.normalize("NFKD", norm_whitesp)

        # normalize captialization
        norm_case = norm_combining.casefold()

        # replace apostrophes with correct one
        norm_apostrophe = norm_case.replace("'", "ʼ").replace("’", "ʼ")

        # get rid of other accents
        norm_noaccent = "".join([
            c for c in norm_apostrophe if c in self._ALPHABET["chars"]
        ])

        return norm_noaccent
    

    def _parse_ending(self, word: Verb, ending: str, position: int) -> list[Verb]:
        '''
        Try to parse given ending from the right of the word
        '''
        parsed_variations = []
        base = word.prefix

        if base.endswith(ending):
            # split it right before the ending
            split_at = len(base) - len(ending)

            # make new word
            if position == self._SUFFIX:
                new_stem = word.stem
                new_suffix = ending + word.suffix
            elif position == self._STEM:
                new_stem = ending + word.stem
                new_suffix = word.suffix
            new_prefix = base[:split_at]

            parsed = Verb(new_prefix, stem=new_stem, suffix=new_suffix)

            # add to list of possible results if successful
            parsed_variations.append(parsed)
                
        return parsed_variations


    def _parse_endings(self, word: Verb, endings: list[str], position: int) -> list[Verb]:
        '''
        Try to parse each ending from the right of the word
        '''
        parsed_variations = []

        for ending in endings:
            # try to parse each ending
            parsed = self._parse_ending(word, ending, position)
            parsed_variations.extend(parsed)
    
        return parsed_variations
    
    def _parse_suffix(self, word: Verb) -> list[Verb]:
        '''
        Try to parse suffix
        '''
        return self._parse_endings(word, self._SUFFIXES["suffixes"], self._SUFFIX)


    def _parse_last_consonant(self, word: Verb) -> list[Verb]:
        '''
        Try to parse rightmost consonant
        '''
        result_mult = self._parse_endings(word, self._CONSONANTS["multiple"], self._STEM)
            
        # if multi-letter consonant is parsed, return without trying to parse one letter
        if len(result_mult) > 0:
            return result_mult

        # otherwise parse one letter only
        return self._parse_endings(word, self._CONSONANTS["single"], self._STEM)


    def _parse_last_vowel(self, word: Verb) -> list[Verb]:
        '''
        Try to parse rightmost vowel
        '''
        result_long = self._parse_endings(word, self._VOWELS["long_high"] + self._VOWELS["long_low"], self._STEM)
            
        # if long vowel is parsed, return without trying to parse short vowel
        if len(result_long) > 0:
            return result_long

        # otherwise parse short vowel
        return self._parse_endings(word, self._VOWELS["short_high"] + self._VOWELS["short_low"], self._STEM)


    def _parse_last_syllable(self, word: Verb) -> list[Verb]:
        '''
        Try to parse a consonant from the end of the word: CVC, CVVC, CV, or CVV
        '''
        # try to parse last consonant which may not exist
        parsed_last_cons = self._parse_last_consonant(word)

        # parse last vowel
        parsed_vowel = []
        if parsed_last_cons:
            for variation in parsed_last_cons:
                parsed_vowel.extend(self._parse_last_vowel(variation))
        parsed_vowel.extend(self._parse_last_vowel(word))

        parsed_syllable = []
        # if vowel parsing fails, then last syllable is invalid so directly return
        if not parsed_vowel:
            return parsed_syllable
        # otherwise, parse first consonant which must exist
        for variation in parsed_vowel:
            parsed_syllable.extend(self._parse_last_consonant(variation))

        return parsed_syllable


    def parse_word(self, word: str, no_display: bool = False) -> list[tuple[str]]:
        '''
        Get possible parsings of a given verb

        params:
            word [str] - the verb, as a string
            no_display [bool] - set to True to suppress output

        returns:
            [list of tuples] - possible parsings in format (prefixes, root, suffixes)
        '''
        # make verb object
        normalized = self._normalize_word(word)
        verb = Verb(normalized)

        # try to parse with suffix
        parsed_suffix = self._parse_suffix(verb)

        # parse last syllable (with and without suffix)
        parsed = []
        if parsed_suffix:
            for variation in parsed_suffix:
                parsed.extend(self._parse_last_syllable(variation))
        parsed.extend(self._parse_last_syllable(verb))

        # convert to friendly representation
        parsed_str = [p.to_string() for p in parsed]
        parsed_roots = [p.stem for p in parsed]
        parsed_result = [p.to_tuple_stem() for p in parsed]

        # displaying the possibilities
        print("verb:", verb)
        print("options:", end="")
        print(", ".join(parsed_str))
        print("verb root options:", end="")
        print(", ".join(parsed_roots))

        return parsed_result
