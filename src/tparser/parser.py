# Copyright (c) 2026 Mona Liu

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Core parser functionality

Classes:
    Parser

Example usage:

    from tparser import Parser

    parser = Parser()
    parser.parse_word("nag̱anáanín")
"""

import json
import unicodedata as ucd
import importlib.resources as rsrc
from collections import deque

from .verb import Verb


class Parser:
    """Parses verbs

    Attributes:
        _ALPHABET (dict): maps "chars" to a list of characters in the alphabet
        _SUFFIXES (dict): maps suffix types to lists of suffixes of that
            type and their properties
        _SUFFIX_TYPES (dict): maps integers to suffix types (in order that they
            appear in `_SUFFIXES`)
        _VOWELS (dict): maps vowel types (length and tone) to lists of vowels
        _CONSONANTS (dict): maps consonant types (short and long) to list of consonants
        _REPLACE_MAP (dict): maps common variations of diacritics to the correct ones
        _VOWEL_MAP (dict): maps long vowels to short vowels
    """

    def __init__(self):
        """Create parser and initialize data"""

        self._ALPHABET = self._load_json("alphabet.json")
        self._SUFFIXES = self._load_json("suffixes.json")
        self._SUFFIX_TYPES = {i: type for i, type in enumerate(self._SUFFIXES)}
        self._VOWELS = self._load_json("vowels.json")
        self._CONSONANTS = self._load_json("consonants.json")
        self._REPLACE_MAP = str.maketrans(
            {
                "\u0332": "\u0331",
                "\u0320": "\u0331",
                "\u0027": "\u02bc",
                "\u2019": "\u02bc",
            }
        )
        self._VOWEL_MAP = {"ee": "i", "ei": "e", "aa": "a", "oo": "u"}

    def _load_json(self, filename: str) -> dict:
        """Read json from a file in the package

        Args:
            filename: file to read

        Returns:
            contents of file
        """
        with (
            rsrc.files("tparser.data")
            .joinpath(filename)
            .open("r", encoding="utf-8") as f
        ):
            return json.load(f)

    def _normalize_word(self, word: str) -> str:
        """Return a normalized form of the verb

        Removes whitespace and accents that are not considered during
        parsing. Also normalizes diacritics and capitalization.

        Args:
            word: a verb

        Returns:
            normalized version of `word`
        """
        # strip whitespace
        norm = word.strip()

        # replace low bar and apostrophe with the right one
        norm = norm.translate(self._REPLACE_MAP)

        # separate combining accents
        norm = ucd.normalize("NFKD", norm)

        # normalize captialization
        norm = norm.casefold()

        # get rid of other accents
        norm = "".join([c for c in norm if c in self._ALPHABET["chars"]])

        return norm

    def _parse_ending(self, word: Verb, ending_list: list[str]) -> list[Verb]:
        """Parse an substring ("ending") from the right of the verb

        Args:
            word: verb to start with
            ending_list: list of endings to try and parse

        Returns:
            list of parsings with any one of the endings from the list parsed,
            empty if none can be parsed
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
                parsed.root_form = word.root_form
                parsed.ablaut = word.ablaut

                # add to list of possible results if successful
                result.append(parsed)

                # check if ending is one of y/w/umlaut y
                if ending in y_variations:
                    y_variations.remove(ending)
                    y_variation_len = len(ending)

        # if y/w/y umlaut are successfully parsed, then add the other options too
        if len(y_variations) < 3:
            for y_variation in y_variations:
                # split it right before the ending
                split_at = len(base) - y_variation_len

                # make new word
                new_stem = y_variation + word.stem
                new_suffix = word.suffix
                new_prefix = base[:split_at]

                parsed = Verb(new_prefix, stem=new_stem, suffix=new_suffix)

                # keep root properties
                parsed.root_form = word.root_form
                parsed.ablaut = word.ablaut

                # add to list of possible results if successful
                result.append(parsed)

        return result

    def _parse_suffix(
        self, word: Verb, suffix_list: list[dict[str, str]]
    ) -> list[Verb]:
        """Parse a rightmost suffix from a list

        Args:
            word: verb to start with
            suffix_list: list of suffixes to try and parse

        Returns:
            list of parsings with any one of the suffixes from the list parsed,
            empty if verb doesn't end with any of them
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
                    parsed.root_form = suffix["form"]
                else:
                    parsed.root_form = word.root_form

                # indicate whether vowel has been changed
                if suffix["ablaut"]:
                    parsed.ablaut = True
                else:
                    parsed.ablaut = word.ablaut

                # add to list of possible results if successful
                result.append(parsed)

        return result

    def _parse_suffixes(self, word: Verb) -> list[Verb]:
        """Parse all possible suffixes
         
        Considers at most one suffix of each type, in the order of
        _SUFFIX_TYPES. Uses depth first search to go through parse tree.

        Args:
            word: verb to start with

        Returns:
            list of parsings with all suffixes parsed, empty if the verb
            does not have a suffix (from the dataset)
        """
        result = []

        q = deque()

        # start with word itself
        q.append((word, -1))

        while q:
            # get next variation and last type of suffix that has been tried
            variation, parsed_type = q.pop()

            # add all "children" (types of suffix after current) to queue
            for i in range(parsed_type + 1, len(self._SUFFIX_TYPES)):
                for next_variation in self._parse_suffix(
                    variation, self._SUFFIXES[self._SUFFIX_TYPES[i]]
                ):
                    q.append((next_variation, i))
                    result.append(next_variation)

        return result

    def _parse_last_consonant(self, word: Verb) -> list[Verb]:
        """Parse rightmost consonant

        Args:
            word: verb to start with

        Returns:
            list of parsings with any one consonant parsed, empty if 
            verb does not end with a consonant
        """
        result_mult = self._parse_ending(word, self._CONSONANTS["multiple"])

        # if multi-letter consonant is parsed, return without trying to parse one letter
        if len(result_mult) > 0:
            return result_mult

        # otherwise parse one letter only
        return self._parse_ending(word, self._CONSONANTS["single"])

    def _parse_last_vowel(self, word: Verb) -> list[Verb]:
        """Parse rightmost vowel

        Args:
            word: verb to start with

        Returns:
            list of parsings with any one vowel parsed, empty if verb does
            not end with a vowel
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
        """Parse an CVC or CVVC syllable from the right of the verb

        Args:
            word: verb to start with

        Returns:
            list of parsings with last syllable parsed, empty if verb
            does not end with a CVC/CVVC syllable
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
        """Parse a CV or CVV syllable from the right of the verb

        Args:
            word: verb to start with

        Returns:
            list of parsings with last syllable parsed, empty if verb
            does not end with a CV/CVV syllable
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

    def _recover_root(self, word: Verb) -> list[Verb]:
        """Undo stem changes to recover possible roots

        Removes tones and changes long vowels to their corresponding short
        vowel. Adds possible roots before ablaut, if applicable

        Args:
            word: parsed verb to recover root from 

        Returns:
            list of parsed verbs with the `root` attribute set
        """
        stem = word.stem
        roots = set()

        # remove high tone
        stem = stem.replace("\u0301", "")

        # change all long vowels to short vowels
        for long, short in self._VOWEL_MAP.items():
            stem = stem.replace(long, short)

        # change vowel back to a or u if ablaut
        if word.ablaut:
            roots.add(stem.replace("e", "a"))
            roots.add(stem.replace("e", "u"))
        roots.add(stem)

        results = [Verb(word.prefix, word.stem, word.suffix, r) for r in roots]

        return results

    def parse_word(
        self, word: str, no_display: bool = False
    ) -> list[tuple[str, str, str]]:
        """Get possible parsings of a given verb

        Args:
            word: the verb, as a string
            no_display: whether the results should be printed ("displayed") 
                in addition to being returned

        Returns:
            Possible parsings in format (prefixes, root, suffixes)
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
                if variation.root_form == "cvc_":
                    parsed.extend(self._parse_last_CVC(variation))
                elif variation.root_form == "cv_":
                    parsed.extend(self._parse_last_CV(variation))
                else:
                    # make sure no roots ending in consonant have ablaut
                    cvc_parsed = self._parse_last_CVC(variation)
                    for p in cvc_parsed:
                        p.ablaut = False
                    parsed.extend(cvc_parsed)

                    parsed.extend(self._parse_last_CV(variation))

        # parse last syllable WITHOUT parsing suffix (no possbility of ablaut)
        parsed.extend(self._parse_last_CVC(verb))
        parsed.extend(self._parse_last_CV(verb))

        final = []
        for p in parsed:
            final.extend(self._recover_root(p))

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
