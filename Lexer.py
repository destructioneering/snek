import re
from enum import Enum

class TokenKind(Enum):
    INDENT = 1
    DEDENT = 2
    IDENT = 3
    PUNCT = 4
    NUM = 5
    STRING = 6

class Token:
    def __init__(self, kind, body):
        self.kind = kind
        self.body = body

class Lexer:
    def __init__(self, iostream):
        self.iostream = iostream

        self.words = [
            [TokenKind.STRING, r'(?:\'.*?\'|".*?")', None],
            [TokenKind.PUNCT, r'[:{}()+\-*/]', None],
            [TokenKind.NUM, r'\d+', None],
            [TokenKind.IDENT, r'\w+', None]
        ]
        for word in self.words:
            word[2] = re.compile(word[1])

        # Build a regex with each token regex in an alternation so the
        # overall expression matches any token. This won't work for
        # all regular expressions, so we have to be careful about what
        # kinds of tokens we support.
        self.mainRegex = ''
        for i, word in enumerate(self.words):
            if i == 0:
                self.mainRegex = '(?:{})'.format(word[1])
            self.mainRegex += '|(?:{})'.format(word[1])
        self.mainRegex = re.compile(self.mainRegex)

    def countIndentation(self, line):
        indent_regex = re.compile(r'^\s+')
        results = re.findall(indent_regex, line)
        if len(results) > 0:
            return len(results[0])
        else:
            return 0

    def splitLine(self, line):
        return re.findall(self.mainRegex, line)

    def interpretWord(self, word):
        for w in self.words:
            if w[2].match(word):
                return Token(w[0], word)

    def tokenize(self):
        oldIndentation = 0
        tokens = []

        for line in self.iostream:
            line = line.rstrip()

            newIndentation = self.countIndentation(line)
            if newIndentation > oldIndentation:
                tokens.append(Token(TokenKind.INDENT, ''))
            if newIndentation < oldIndentation:
                tokens.append(Token(TokenKind.DEDENT, ''))
            oldIndentation = newIndentation

            for word in self.splitLine(line):
                tokens.append(self.interpretWord(word))

        self.tokens = tokens

    def dump(self):
        for token in self.tokens:
            print(f"{token.kind:<20} {token.body}")
