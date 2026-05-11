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
"""Representations of verbs for internal use

Classes:
    Verb
"""


class Verb:
    """Represent verb parsings

    Represents verb as prefix, stem, suffix. Also includes the
    parsed root and information like form, tone, phonetic/orthographic
    changes, etc.

    Attributes:
        prefix (str): un-parsed part of the verb
        stem (str): part of the verb that corresponds to the root
        suffix (str): parsed suffixes
        root (str): stem after removing changes such as tone and vowel length
        root_form (str): whether the root is CV or CVC, based on suffixes
        ablaut (bool): whether the root may have been ablaut-ed, based on suffixes
    """

    def __init__(
        self, prefix_or_full: str, stem: str = "", suffix: str = "", root: str = ""
    ):
        """Initializes verb object

        If one argument is given, it is set as the prefix.
        If stem or suffix are given, they are set accordingly.

        Args:
            prefix_or_full: prefix or the entire verb
            stem: stem
            suffix: suffixes as one string
            root: the root, if known
        """
        self.prefix = prefix_or_full
        self.stem = stem
        self.suffix = suffix
        self.root = root

        self.root_form = ""
        self.ablaut = False

    def __str__(self) -> str:
        """Simple string representation

        Returns:
            prefix, stem, and suffix concatenated
        """
        return self.prefix + self.stem + self.suffix

    def to_string(self, sep_char: str = "|") -> str:
        """Fancy string representation

        Args:
            sep_char: character to indicate each part of the verb

        Returns:
            prefix, stem, and suffix separated by `sep_char`
        """
        return sep_char.join([self.prefix, self.stem, self.suffix]).strip(sep_char)

    def to_tuple_root(self) -> tuple[str, str, str]:
        """Tuple representation with root as 2nd item

        Returns:
            (prefix, root, suffix) tuple
        """
        return (self.prefix, self.root, self.suffix)

    def to_tuple_stem(self) -> tuple[str, str, str]:
        """Tuple representation with stem as 2nd item

        Returns:
            (prefix, stem, suffix) tuple
        """
        return (self.prefix, self.stem, self.suffix)
