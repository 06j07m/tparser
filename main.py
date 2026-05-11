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
"""Functions to develop, debug, and test the parser

Functions:
    extract_text_data
    test_parser
    main
"""


from tparser import Parser
import pandas as pd


def extract_test_data(filepath: str) -> tuple[list[str], list[str]]:
    """Extract test data into corresponding lists

    Extract test data from CSV file into list of verbs and list
     of corresponding verb roots. Verb column must be named "verb" 
     and root column must be named "root"

    Args:
        filepath: path to CSV file

    Returns:
        (list of verbs, list of roots)
    """
    # read csv into dataframe
    data_df = pd.read_csv(filepath)

    # get columns
    verb_col = data_df.loc[:, "verb"]
    root_col = data_df.loc[:, "root"]

    return verb_col.to_list(), root_col.to_list()


def test_parser(verbs: list[str], true_answers: list[str], filepath: str) -> None:
    """Tests parser on given list of verbs

    Parses each verb in list and compares to actual root, and
    saves results to Excel file

    Args:
        verbs: list of verbs to test on
        true_answers: list of actual roots corresponding to each verb
        filepath: path of Excel file to save results to

    Returns:
        None
    """
    parser = Parser()

    pred_answers = []

    for i in range(len(verbs)):
        verb = verbs[i]
        actual_root = parser._normalize_word(true_answers[i])
        pred = parser.parse_word(verb, no_display=True)
        pred_roots = [p[1] for p in pred]
        result = actual_root in pred_roots

        pred_answers.append(
            {
                "verb": verb,
                "actual_root": actual_root,
                "parsed_roots": pred_roots,
                "success": result,
            }
        )

    results_df = pd.DataFrame(pred_answers)
    results_df.to_excel(filepath, index=False)


def main():
    # extract data
    test_verbs, test_roots = extract_test_data("tests/test_data_swanton.csv")
    test_verbs_2, test_roots_2 = extract_test_data("tests/test_data_eggleston.csv")
    all_test_verbs = test_verbs + test_verbs_2
    all_test_roots = test_roots + test_roots_2

    #testing
    parser = Parser()
    parser.parse_word("nag̱anáanín")
    test_parser(all_test_verbs, all_test_roots, "asdf.xlsx")


if __name__ == "__main__":
    main()
