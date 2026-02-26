class Verb:
    '''
    Class to represent verbs
    Three sections: prefixes, stem, and suffixes
    Plus verb root
    '''
    
    @classmethod
    def init_separate(cls, word: str) -> Verb:
        '''
        Set up word given full word (puts everything in stem)
        '''
        return Verb("", word, [])


    def __init__(self, prefix: str, stem: str, suffix: list[str]) -> None:
        '''
        Set up word given components
        '''
        self.pre = prefix
        self.stem = stem
        self.suf = suffix
        self.root = ""


    def __str__(self) -> str:
        '''
        returns the entire word
        '''
        return self.pre + self.stem + "".join(self.suf)
