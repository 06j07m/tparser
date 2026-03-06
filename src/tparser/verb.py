class Verb:
    """
    Object to represent verbs
    """

    def __init__(self, prefix_or_full: str, stem: str = "", suffix: str = "", root: str = ""):
        '''
        Create verb from given stem and optional prefix, suffix, root
        (If not provided, the entire word becomes the stem)
        '''
        self.prefix = prefix_or_full
        self.stem = stem
        self.suffix = suffix
        self.root = root

    def __str__(self) -> str:
        '''
        Return simple string representation
        '''
        return self.prefix + self.stem + self.suffix
    
    def to_string(self) -> str:
        '''
        Return fancy string representation
        '''
        return "|".join([self.prefix, self.stem, self.suffix]).strip("|")
    
    def to_tuple_root(self) -> tuple[str, str, str]:
        '''
        Return tuple representation with root as 2nd item
        '''
        return (self.prefix, self.root, self.suffix)

    def to_tuple_stem(self) -> tuple[str, str, str]:
        '''
        Return tuple representation with stem as 2nd item
        '''
        return (self.prefix, self.stem, self.suffix)


