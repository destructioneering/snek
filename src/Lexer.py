import re
from enum import Enum

from Token import Token

class Lexer:
    def __init__(self, code):
        self.code = code

        self.words = [
            ['STRING', r'(?:\'.*?\'|".*?")', None],
            ['PUNCT', r'(?:/=|\*=|-=|\+=|>=|<=|!=|==|\*\*|[.%<>=,:{}()+\-*/^])', None],
            ['NUM', r'\d+', None],
            ['IDENT', r'\w+', None]
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
        self.commentRegex = re.compile(r'^\s*#')

    def countIndentation(self, line):
        indent_regex = re.compile(r'^\s+')
        results = re.findall(indent_regex, line)
        if len(results) > 0:
            return int(len(results[0]) / 4)
        else:
            return 0

    def splitLine(self, line):
        return re.findall(self.mainRegex, line)

    def interpretWord(self, word):
        for w in self.words:
            if w[2].match(word):
                return Token(w[0], word, False)

    def tokenize(self):
        oldIndentation = 0
        tokens = []

        for line in self.code.splitlines():
            line = line.rstrip()

            if len(line) == 0: continue
            if self.commentRegex.match(line): continue

            newIndentation = self.countIndentation(line)
            for i in range(abs(newIndentation - oldIndentation)):
                if newIndentation > oldIndentation:
                    tokens.append(Token('INDENT', '', True))
                if newIndentation < oldIndentation:
                    tokens.append(Token('DEDENT', '', True))
            oldIndentation = newIndentation

            if len(line) == 0: continue

            for i, word in enumerate(self.splitLine(line)):
                tokens.append(self.interpretWord(word))
                if i == 0:
                    tokens[-1].lineStart = True

        while oldIndentation > 0:
            tokens.append(Token('DEDENT', '', True))
            oldIndentation -= 1

        self.tokens = tokens

    def dump(self):
        for token in self.tokens:
            print(f"{token.kind:<20} {token.body}")
