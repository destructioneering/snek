#!/usr/bin/env python3

import sys
from Lexer import Lexer

if __name__ == '__main__':
    lexer = Lexer(sys.stdin)
    lexer.tokenize()
    lexer.dump()
    for token in lexer.nextToken():
        print(f'{token.body}')
