#!/usr/bin/env python3

import sys
from Lexer import Lexer
from Parser import Parser

if __name__ == '__main__':
    lexer = Lexer(sys.stdin)
    lexer.tokenize()
    # lexer.dump()
    parser = Parser(lexer)
    parser.parse()
    parser.dump()
