import pandas as pd

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


# ALPHABET AND SYLLABLE CONSTANTS (?)    
consonants = ["d", "t", "t'", "n", "s", "s'", "dz", "ts", "ts'", "sh", "j", "ch", "ch'",
                "l", "l'", "dl", "tl", "tl'", "y", "g", "k'", "x", "x'", "gw", "kw", "k'w",
                "xw", "x'w", "w", "g̲", "ḵ", "ḵ'", "x̲", "x̲'", "g̲w", "ḵw", "ḵ'w", "x̲w",
                "x̲'w", ".", "h"]

vowels = ["i", "e", "a", "u"]
vowels_long = ["ee", "ei", "aa", "oo"]
vowels_high = ["í", "é", "á", "ú"]
vowels_high_long = ["ée", "éi", "áa", "óo"]

suffixes = extract_suffixes("suffixes.csv", "suffix")


# BASIC PARSING STEPS (?)
def parse_ending(word: list[str], ending: str) -> tuple[bool, list[str]]:
    '''
    Parse 0 or 1 repetitions of the ending from the right of the word
    '''
    base = word[0]

    if base.endswith(ending):
        # split it right before the ending
        split_at = len(base) - len(ending)
        parsed = [base[:split_at], base[split_at:]]

        # if there are other parts that are already split, add them
        if len(word) > 1:
            parsed.append(word[1:][0])
    else:
        parsed = []

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
            if parse_success:
                parsed_variations.append(parsed)

    # also add unchanged version
    parsed_variations.append(word)

    # signal whether parsing worked or not
    parse_success = len(parsed_variations) > 1

    return parse_success, parsed_variations


def parse_suffix(word: list[list[str]]) -> list[list[str]]:
    '''
    Parse suffix from word variations
    '''
    parse_success, result = parse_endings(word, suffixes)
    return result


def parse_consonant_right(word: list[list[str]]) -> list[list[str]]:
    '''
    Parse last consonant from word variations
    '''
    parse_success, result = parse_endings(word, consonants)
    return result


def parse_vowel_right(word: list[list[str]]) -> list[list[str]]:
    '''
    Parse suffix from word variations
    '''
    parse_success, result_long = parse_endings(word, 
                                               vowels_long + vowels_high_long)
          
    # if long vowel is parsed, return without trying to parse short vowel
    if parse_success:
       return result_long

    parse_success, result_short = parse_endings(word,
                                                vowels + vowels_high)
    return result_long


# TESTING
def parse_word(word: list[list[str]]) -> list[list[str]]:
    set1 = parse_suffix(word)
    print("suffix", set1)
    set2 = parse_consonant_right(set1)
    print("last cons", set2)
    set3 = parse_vowel_right(set2)
    print("vowel", set3)
    set4 = parse_consonant_right(set3)
    print("2nd last cons", set4)

    return set4


if __name__ == "__main__":
    test_verbs, test_roots = extract_test_data("test_data_swanton.csv")

    for verb in test_verbs:
        print("original", [[verb]])
        parse_word([[verb]])
        print("-----------------")