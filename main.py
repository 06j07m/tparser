from tparser import Parser
import pandas as pd


def extract_test_data(filepath: str) -> tuple[list[str], list[str]]:
    """
    Extract test data into list of verbs and list of corresponding verb roots
    Verb column must be named "verb" and root column must be named "root"
    """
    # read csv into dataframe
    data_df = pd.read_csv(filepath)

    # get columns
    verb_col = data_df.loc[:, "verb"]
    root_col = data_df.loc[:, "root"]

    return verb_col.to_list(), root_col.to_list()


def main():
    test_verbs, test_roots = extract_test_data("tests/test_data_swanton.csv")
    test_verbs_2, test_roots_2 = extract_test_data("tests/test_data_eggleston.csv")
    all_test_verbs = test_verbs + test_verbs_2
    all_test_roots = test_roots + test_roots_2

    parser = Parser()

    results = []

    for i in range(len(all_test_verbs)):
        verb = all_test_verbs[i]
        actual_root = parser._normalize_word(all_test_roots[i])
        pred = parser.parse_word(verb, no_display=True)
        pred_roots = [p[1] for p in pred]
        result = actual_root in pred_roots

        results.append(
            {
                "verb": verb,
                "actual_root": actual_root,
                "parsed_roots": pred_roots,
                "success": result,
            }
        )

    results_df = pd.DataFrame(results)
    results_df.to_excel("test_results.xlsx", index=False)


if __name__ == "__main__":
    main()
