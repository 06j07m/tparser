import pandas as pd
import unicodedata as ucd
import json


# ALPHABET AND SYLLABLE CONSTANTS + SUFFIX LIST
with open("alphabet.json", "r") as alphabet_file:
    ALPHABET = json.load(alphabet_file)
with open("suffixes.json", "r") as suffixes_file:
    SUFFIXES = json.load(suffixes_file)
with open("vowels.json", "r") as vowels_file:
    VOWELS = json.load(vowels_file)
with open("consonants.json", "r") as consonants_file:
    CONSONANTS = json.load(consonants_file)


# HELPER FUNCTIONS
def extract_test_data(filepath: str) -> tuple[list[str], list[str]]:
    '''
    Extract test data into list of verbs and list of corresponding verb roots
    Verb column must be named "verb" and root column must be named "root"
    '''
    # read csv into dataframe
    data_df = pd.read_csv(filepath)

    # get columns
    verb_col = data_df.loc[:, "verb"]
    root_col = data_df.loc[:, "root"]

    return verb_col.to_list(), root_col.to_list()


def print_word(word: list[list[str]]) -> None:
    print(["|".join(w).strip("|") for w in word])


def print_word_roots(word: list[list[str]]) -> None:
    print([w[1] for w in word])


# NORMALIZATION FUNCTIONS
def normalize_str(word: str) -> str:
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
        c for c in norm_apostrophe if c in ALPHABET["chars"]
    ])

    return norm_noaccent


# BASIC PARSING
def parse_ending(word_variations: list[list[str]], ending: str, loc: int) -> list[list[str]]:
    '''
    Try to parse given ending from the right of the word
    '''
    parsed_variations = []

    for word in word_variations:
        base = word[0]

        # make new word template from old one
        parsed = [w for w in word]

        if base.endswith(ending):
            # split it right before the ending
            split_at = len(base) - len(ending)
            
            # update base and specified location to put the ending
            parsed[0] = base[:split_at]
            parsed[loc] = base[split_at:] + parsed[loc]

             # add to list of possible results if successful
            parsed_variations.append(parsed)
            
    return parsed_variations


def parse_endings(word_variations: list[list[str]], endings: list[str], loc: int) -> list[list[str]]:
    '''
    Try to parse each ending from the right of the word
    '''
    parsed_variations = []

    for endg in endings:
        # try to parse each ending
        parsed = parse_ending(word_variations, endg, loc)

        # prevent duplicates being added
        if parsed not in parsed_variations:
            parsed_variations.extend(parsed)
 
    return parsed_variations


# MORE PARSING
def parse_suffix(word_variations: list[list[str]]) -> list[list[str]]:
    '''
    Parse suffix from word variations
    '''
    return parse_endings(word_variations, SUFFIXES["suffixes"], 2)


def parse_last_consonant(word: list[list[str]]) -> list[list[str]]:
    '''
    Parse last consonant from word variations
    '''
    result_mult = parse_endings(word, CONSONANTS["multiple"], 1)
          
    # if multi-letter consonant is parsed, return without trying to parse one letter
    if len(result_mult) > 0:
       return result_mult

    # otherwise parse one letter only
    return parse_endings(word, CONSONANTS["single"], 1)


def parse_last_vowel(word: list[list[str]]) -> list[list[str]]:
    '''
    Parse last vowel from word variations
    '''
    result_long = parse_endings(word, VOWELS["long_high"] + VOWELS["long_low"], 1)
          
    # if long vowel is parsed, return without trying to parse short vowel
    if len(result_long) > 0:
       return result_long

    # otherwise parse short vowel
    return parse_endings(word, VOWELS["short_high"] + VOWELS["short_low"], 1)


def parse_last_syllable(word: list[list[str]]) -> list[list[str]]:
    '''
    Try to parse a consonant from the end of the word: CVC, CVVC, CV, or CVV
    '''
    # try to parse last consonant which may not exist
    end_result = parse_last_consonant(word)

    # parse last vowel
    if end_result:
        mid_result = parse_last_vowel(end_result)
    else:
        mid_result = []
    mid_result.extend(parse_last_vowel(word))

    # if vowel parsing fails, then last syllable is invalid
    if not mid_result:
        return []
    
    # otherwise, parse first consonant which must exist
    start_result = parse_last_consonant(mid_result)

    return start_result


def parse_word(word: str) -> list[list[str]]:
    normalized = [[normalize_str(word), "", ""]]

    # try to parse with suffix
    with_suffix = parse_suffix(normalized)

    if with_suffix:
        with_root = parse_last_syllable(with_suffix)
    else:
        with_root = []
    with_root.extend(parse_last_syllable(normalized))
    
    return with_root


# TESTING
if __name__ == "__main__":
    test_verbs, test_roots = extract_test_data("test_data_swanton.csv")
    for i in range(len(test_verbs)):
        verb = test_verbs[i]
        result = parse_word(verb)
        print("verb:", print(verb))
        print("options:", end="")
        print_word(result)
        print("verb root options:", end="")
        print_word_roots(result)
        print("actual:", test_roots[i])
        print("---------------")