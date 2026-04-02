# tparser

## About

A Python package for parsing verb roots in Tlingit. Currently rule-based only.

## Installation

The easiest way is to install it is from the latest release in [Releases](https://github.com/06j07m/tparser/releases).

Please make sure you have Python 3.10 or later installed. If using a virtual environment, please make sure it is active!

Navigate to your project folder and run 

```shell
pip install https://github.com/06j07m/tparser/releases/download/v0.3.0/tparser-0.3.0-py3-none-any.whl
```

Alternatively, you can download the `.whl` file and install from the downloaded file. Just replace the URL in the command above with the path to the file.

## Usage

Sample usage:

```python
>>> from tparser import Parser
>>> parser = Parser()
>>> parser.parse_word("akaawaník")
verb: akaawaník
options: akaa|wan|ík, akaawa|ní|k, akaawa|ník
verb root options: wan, ni, nik
[('akaa', 'wan', 'ík'), ('akaawa', 'ni', 'k'), ('akaawa', 'nik', '')]
```

See the [project wiki](https://github.com/06j07m/tparser/wiki) for full documentation.