from enum import Enum
import json

from Statement import *
from Expression import *
from ExpressionParser import ExpressionParser
from Token import Token

class DedentException(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tokenIndex = 0

    def putTokenBack(self):
        self.tokenIndex -= 1
        return self.tokens[self.tokenIndex]

    def token(self):
        return self.tokens[self.tokenIndex] if self.tokenIndex < len(self.tokens) else None

    def nextToken(self):
        self.tokenIndex += 1
        if self.tokenIndex >= len(self.tokens): return None
        return self.tokens[self.tokenIndex]

    def error(self, errorString):
        print(f"Parse error: {errorString}: ({self.token().body})")

    def expect(self, condition, errorString):
        if not condition:
            self.error(errorString)

    def parseExpression(self):
        expressionParser = ExpressionParser(self.tokens[self.tokenIndex:])
        node = expressionParser.parse()
        self.tokenIndex += expressionParser.tokenIndex
        return node

    def parseStatementList(self):
        statements = []
        while not self.token().dedent():
            try:
                statement = self.parseStatement()
            except DedentException:
                break
            statements.append(statement)
        return statements

    def parseElseElif(self):
        """Returns either an IfStatement or some other kind of statement."""
        if self.token() and self.token().ident() == 'elif':
            self.nextToken()
            elsecondition = self.parseExpression()
            self.expect(self.token().punct() == ':', 'Expected a `:`')
            self.nextToken()    # Skip the :
            self.expect(self.token().indent(), 'Expected an indent')
            self.nextToken()    # Skip the indent
            elsebody = self.parseStatementList()
            self.expect(self.token().dedent(), 'Expected a dedent')
            self.nextToken()
            return IfStatement(elsecondition, elsebody, self.parseElseElif())
        elif self.token() and self.token().ident() == 'else':
            self.nextToken()
            self.expect(self.token().punct() == ':', 'Expected a `:`')
            self.nextToken()    # Skip the :
            self.expect(self.token().indent(), 'Expected an indent')
            self.nextToken()    # Skip the indent
            elsebody = self.parseStatementList()
            self.expect(self.token().dedent(), 'Expected a dedent')
            self.nextToken()
            return elsebody

        return None

    def parseIf(self):
        self.nextToken()
        condition = self.parseExpression()
        self.expect(self.token().punct() == ':', 'Expected `:`')
        self.nextToken()
        self.expect(self.token().indent(), 'Expected an indent')
        self.nextToken()
        body = self.parseStatementList()
        self.expect(self.token().dedent(), 'Expected a dedent')
        self.nextToken()
        return IfStatement(condition, body, self.parseElseElif())

    def parseWhile(self):
        self.nextToken()
        condition = self.parseExpression()
        self.expect(self.token().punct() == ':', 'Expected `:`')
        self.nextToken()
        self.expect(self.token().indent(), 'Expected an indent')
        self.nextToken()
        body = self.parseStatementList()
        self.expect(self.token().dedent(), 'Expected a dedent')
        self.nextToken()
        return WhileStatement(condition, body)

    def parsePrint(self):
        self.nextToken()
        return PrintStatement(self.parseExpression())

    def parseReturn(self):
        self.nextToken()
        return ReturnStatement(self.parseExpression())

    def parseFunctionParameters(self):
        token = self.nextToken()
        if token.ident() == None: return []
        parameters = [token.ident()]

        while True:
            token = self.nextToken()
            if token.punct() == ',':
                token = self.nextToken()
                self.expect(token.ident() != None, 'Expected an identifier in argument list')
                parameters.append(token.ident())
            else:
                break

        return parameters

    def parseFunction(self):
        self.nextToken()
        self.expect(self.token().ident() != None, 'Expected an identifier')
        identifier = self.token()
        self.nextToken()
        self.expect(self.token().punct() == '(', 'Expected a `(`')
        parameters = self.parseFunctionParameters()
        self.expect(self.token().punct() == ')', 'Expected a `)`')
        self.nextToken()
        self.expect(self.token().punct() == ':', 'Expected a `:`')
        self.nextToken()
        self.expect(self.token().indent(), 'Expected an indent at start of function body')
        self.nextToken()
        body = self.parseStatementList()
        self.expect(self.token().dedent(), 'Expected a dedent at end of function body')
        self.nextToken()
        return FunctionStatement(identifier.ident(), parameters, body)

    def parseClass(self):
        self.nextToken()
        self.expect(self.token().ident() != None, 'Expected an identifier')
        identifier = self.token()
        self.nextToken()
        self.expect(self.token().punct() == ':', 'Expected a `:`')
        self.nextToken()
        self.expect(self.token().indent(), 'Expected an indent at start of class body')
        self.nextToken()
        body = self.parseStatementList()
        self.expect(self.token().dedent(), 'Expected a dedent at end of class body')
        self.nextToken()
        return ClassStatement(identifier.ident(), body)

    def parseExpressionStatement(self):
        return ExpressionStatement(self.parseExpression())

    def parseStatement(self):
        """
        Reads a statement from the token stream. Returns a `Node`.
        """
        token = self.token()

        if token == None: return None

        if token.ident() == 'if':
            return self.parseIf()
        elif token.ident() == 'while':
            return self.parseWhile()
        elif token.ident() == 'print':
            return self.parsePrint()
        elif token.ident() == 'def':
            return self.parseFunction()
        elif token.ident() == 'return':
            return self.parseReturn()
        elif token.ident() == 'class':
            return self.parseClass()
        elif token.dedent():
            raise DedentException()
        elif token.ident() != None: # Could be an assignment
            equalSign = self.nextToken()

            # Check to see if this is a variable assignment
            if equalSign.punct() == '=':
                self.nextToken()
                return AssignStatement(token.ident(), self.parseExpression())
            else:
                self.putTokenBack()
                return self.parseExpressionStatement()
        else:
            return self.parseExpressionStatement()

        self.error('Expected a statement')

    def dump(self):
        """
        Pretty print the AST.
        """
        #print(jsonpickle.encode(self.statements))
        pass

    def parse(self):
        """
        Parses the token stream into an AST.
        """
        self.statements = []

        while True:
            try:
                statement = self.parseStatement()
            except DedentException:
                break
            if statement == None: break
            self.statements.append(statement)
