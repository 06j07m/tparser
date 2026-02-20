from basic_parser import BasicParser

parser = BasicParser()

verbs, roots = BasicParser.extract_test_data("test_data_eggleston.csv")

for v in verbs:
	input_word = [[v]]
	print(parser.parse_suffix(input_word))