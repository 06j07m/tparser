import pandas as pd

class BasicParser:

    # HELPER FUNCTIONS
    def extract_suffixes(filepath: str, column : str) -> list[str]:
        '''
        Extract suffixes from a CSV given file name and column name
        '''
        # read csv into dataframe
        suffix_df = pd.read_csv(filepath)

        # get column as list
        suffix_column = suffix_df.loc[column]

        return list(column)


    def extract_test_data(filepath: str) -> tuple(list(str), (str)):
        '''
        Extract test data into list of verbs and list of corresponding verb roots
        Verb column must be named "verb" and root column must be named "root"
        '''
        # read csv into dataframe
        data_df = pd.read_csv(filepath)

        # get columns
        verb_col = data_df.loc["verb"]
        root_col = data.df.loc["root"]

        return list(verb_col), list(root_col)


    def extract_onecol_csv(filepath: str) -> list(str):
        '''
        Extract the data from an arbitrary CSV file that only contains one column
        '''
        # read csv into dataframe
        df = pd.read_csv(filepath)

        # get first column and return it
        return df.iloc[:,0]
    

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

    
    # CONSTRUCTOR

    # def __init__(self):
        

    # BASIC PARSING STEPS (?)

    def parse_suffix(self, word: list(list(str))) -> list(list(str)):
        '''
        Parse suffix from word variations
        '''
        result_word = []

        for w in word:
            modified = False
            for sf in suffixes:
                if w[0].endswith(sf):
                    split_at = len(w[0]) - len(sf)
                    result_word.append([w[0][split_at:], w[0][:split_at], w[1:]])
                    modified = True
            if not modified:
                result_word.append(w)

        return result_word
