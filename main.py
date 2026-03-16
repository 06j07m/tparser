from tparser import Parser
import pandas as pd

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

if __name__ == "__main__":
    test_verbs, test_roots = extract_test_data("tests/test_data_swanton.csv")
    parser = Parser()
    
    for i in range(20):
        verb = test_verbs[i]
        result = parser.parse_word(verb)
        print("actual:", test_roots[i])
        print("---------------")