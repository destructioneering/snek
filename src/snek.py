#!/usr/bin/env python3

import logging, sys
from Lexer import Lexer
from Parser import Parser
from Evaluator import Evaluator

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    lexer = Lexer(sys.stdin.read())
    lexer.tokenize()
    # lexer.dump()
    parser = Parser(lexer.tokens)
    parser.parse()
    # parser.dump()
    evaluator = Evaluator()
    for statement in parser.statements:
        evaluator.eval(statement)
    evaluator.cleanUp()

    logging.info('The following objects remain:')

    for obj in evaluator.gc.objects:
        if obj.referenceCount < 1: continue
        logging.info(obj)
