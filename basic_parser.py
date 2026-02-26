import pandas as pd
import unicodedata as ucd

# HELPER FUNCTIONS
def extract_suffixes(filepath: str, column : str) -> list[str]:
    '''
    Extract suffixes from a CSV given file name and column name
    '''
    # read csv into dataframe
    suffix_df = pd.read_csv(filepath)

    # get column as list
    suffix_column = suffix_df.loc[:, column]

    # only unique values
    return suffix_column.unique().tolist()


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


def extract_onecol_csv(filepath: str) -> list[str]:
    '''
    Extract the data from an arbitrary CSV file that only contains one column
    '''
    # read csv into dataframe
    df = pd.read_csv(filepath)

    # get first column and return it
    return df.iloc[:,0].to_list()


def print_word(word: list[list[str]]) -> None:
    print(["-".join(w) for w in word])


# ALPHABET AND SYLLABLE CONSTANTS (?)    
consonants_mult = ["dz", "ts", "tsʼ", "sh", "ch", "chʼ", "dl", "tl", "tlʼ", "gw", 
                   "kw", "kʼw", "xw", "xʼw", "g̱w", "ḵw", "ḵʼw", "x̱w", "x̱ʼw"]
consonants_single = ["d", "t", "tʼ", "n", "s", "sʼ", "j", "l", "lʼ", "y", "g", "kʼ", 
                     "x", "xʼ", "w", "g̱", "ḵ", "ḵʼ", "x̱", "x̱ʼ", ".", "h"]

vowels_long = ["ee", "ei", "aa", "oo"]
vowels_high_long = ["ée", "éi", "áa", "óo"]
vowels = ["i", "e", "a", "u"]
vowels_high = ["í", "é", "á", "ú"]

suffixes = extract_suffixes("suffixes.csv", "suffix")


# BASIC PARSING STEPS (?)
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
        c for c in norm_apostrophe if ucd.combining(c) and c != "̱"
    ])

    return norm_noaccent


def parse_ending(word: list[str], ending: str) -> tuple[bool, list[str]]:
    '''
    Parse 0 or 1 repetitions of the ending from the right of the word
    '''
    base = word[0]
    
    parsed = []

    if base.endswith(ending):
        # split it right before the ending
        split_at = len(base) - len(ending)
        parsed.append(base[:split_at])
        parsed.append(base[split_at:])

        # if there are other parts that are already split, add them
        if len(word) > 1:
            parsed.extend(word[1:])

    # signal whether parsing worked or not
    parse_success = len(parsed) > 0

    return parse_success, parsed


def parse_endings(word_variations: list[list[str]], endings: list[str]) -> tuple[bool, list[list[str]]]:
    '''
    Parse 0 or 1 repetitions of each ending from the end of each variation
    of the word
    '''
    parsed_variations = []

    for word in word_variations:
        for endg in endings:
            parse_success, parsed = parse_ending(word, endg)
            if parse_success and parsed not in parsed_variations:
                parsed_variations.append(parsed)
                
    # signal whether parsing worked or not
    parse_success = len(parsed_variations) > 0

    return parse_success, parsed_variations


def parse_suffix(word: list[list[str]]) -> tuple[bool, list[list[str]]]:
    '''
    Parse suffix from word variations
    '''
    return parse_endings(word, suffixes)


def parse_last_consonant(word: list[list[str]]) -> tuple[bool, list[list[str]]]:
    '''
    Parse last consonant from word variations
    '''
    parse_success, result_mult = parse_endings(word, consonants_mult)
          
    # if multi-letter consonant is parsed, return without trying to parse one letter
    if parse_success:
       return parse_success, result_mult

    # otherwise parse one letter only
    return parse_endings(word, consonants_single)


def parse_last_vowel(word: list[list[str]]) -> tuple[bool, list[list[str]]]:
    '''
    Parse last vowel from word variations
    '''
    parse_success, result_long = parse_endings(word, vowels_long + vowels_high_long)
          
    # if long vowel is parsed, return without trying to parse short vowel
    if parse_success:
       return parse_success, result_long

    # otherwise parse short vowel
    return parse_endings(word, vowels + vowels_high)


def parse_last_syllable(word: list[list[str]]) -> tuple[bool, list[list[str]]]:
    '''
    Try to parse a consonant from the end of the word: CVC, CVVC, CV, or CVV
    '''
    # parse last consonant if it exists
    parse_end_con_success, parsed_end_con = parse_last_consonant(word)

    # parse vowel depending on whether consonant was parsed or not
    if parse_end_con_success:
        parse_vowel_success, parsed_vowel = parse_last_vowel(parsed_end_con)        
    else:
        parse_vowel_success, parsed_vowel = parse_last_vowel(word)

    # if vowel wasn't parsed, invalid
    if not parse_vowel_success:
        return False, []
    
    # if vowel successfully parsed, continue with parsing first consonant
    return parse_last_consonant(parsed_vowel)


# def parse_word(word: list[list[str]]) -> list[list[str]]:
#     parse_suffix()


# TESTING
if __name__ == "__main__":
    test_verbs, test_roots = extract_test_data("test_data_swanton.csv")

    for verb in test_verbs[:10]:
        print(verb)
        print(">>>> ", parse_last_syllable([[normalize_str(verb)]]))
        print("---------------")