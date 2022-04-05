from enum import Enum
import json
import jsonpickle

class Expression:
    def __init__(self, kind, body):
        """
        `body` is the token string associated with this expression.
        e.g. '+' for an expression like `a+b`.
        """
        self.kind = kind
        self.body = body
        self.children = {}

    def addChild(self, k, v):
        self.children[k] = v

class Node:
    def __init__(self, kind):
        self.kind = kind
        self.children = {}

    def addChild(self, k, v):
        self.children[k] = v

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.tokenGenerator = lexer.getGenerator()

    def nextToken(self):
        return next(self.tokenGenerator, None)

    def error(self, errorString):
        print(f"Parse error: {errorString} / {self.nextToken().body}")

    def expect(self, token, errorString):
        if self.nextToken().body != token:
            self.error(errorString)

    def expectKind(self, tokenKind, errorString):
        if self.nextToken().kind != tokenKind:
            self.error(errorString)

    def parseExpression(self):
        token = self.nextToken()
        if token.kind == 'IDENT' and token.body == 'true':
            return Expression('BOOL', token.body)
        if token.kind == 'STRING':
            return Expression('STRING', token.body)
        self.error('Unsupported expression')

    def parseIf(self):
        condition = self.parseExpression()
        self.expect(':', 'Expected `:`')
        self.expectKind('INDENT', 'Expected an indent')
        body = self.parseStatement()
        self.expectKind('DEDENT', 'Expected a dedent')
        node = Node('IF')
        node.addChild('condition', condition)
        node.addChild('body', body)
        return node

    def parsePrint(self):
        expression = self.parseExpression()
        node = Node('PRINT')
        node.addChild('expression', expression)
        return node

    def parseStatement(self):
        """
        Reads a statement from the token stream. Returns a `Node`.
        """
        token = self.nextToken()

        if token == None: return None

        if token.body == 'if':
            return self.parseIf()
        elif token.body == 'print':
            return self.parsePrint()

        self.error('Expected a statement')

    def dumpStatement(self, statement):
        print(f"{statement.kind}")

    def dump(self):
        """
        Pretty print the AST.
        """
        self.indentDepth = 0

        print(jsonpickle.encode(self.statements))

        return

        for statement in self.statements:
            self.dumpStatement(statement)

    def parse(self):
        """Parses the token stream into an AST."""
        self.statements = []

        while True:
            statement = self.parseStatement()
            if statement == None: break
            self.statements.append(statement)
