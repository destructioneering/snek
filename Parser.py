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
        self.tokens = [token for token in lexer.getGenerator()]
        self.tokenIndex = 0

    def putTokenBack(self):
        self.tokenIndex -= 1
        return self.tokens[self.tokenIndex]

    def getCurrentToken(self):
        return self.tokens[self.tokenIndex - 1]

    def nextToken(self):
        if self.tokenIndex >= len(self.tokens): return None
        self.tokenIndex += 1
        return self.tokens[self.tokenIndex - 1]

    def error(self, errorString):
        print(f"Parse error: {errorString}: ({self.getCurrentToken().body})")

    def expect(self, token, errorString):
        if self.nextToken().body != token:
            self.error(errorString)

    def expectKind(self, tokenKind, errorString):
        if self.nextToken().kind != tokenKind:
            self.error(errorString)

    def expectToken(self, tokenKind, tokenBody, errorString):
        token = self.nextToken()
        if token.kind != tokenKind or token.body != tokenBody:
            self.error(errorString)

    def shuntingYard(self):
        operators = {
            # Each tuple is just (precedence, right associative?).
            '^': (4, True),
            '*': (3, False),
            '/': (3, False),
            '+': (2, False),
            '-': (2, False),
            '(': (0,),
        }

        constants = {
            'pi': 3.1415926,
            'π': 3.1415926,
        }

        stack = []
        output = []
        tokensConsumed = 0

        while True:
            c = self.nextToken()
            tokensConsumed += 1

            if c == None: break

            # print('input: {}\n\tstack: {}\n\toutput: {}'.format(c.body, stack, output))

            if c.kind == 'IDENT' and (c.body == 'true' or c.body == 'false'):
                stack.append(c.body == 'true')
                continue

            if c.kind != 'PUNCT' and c.kind != 'NUM' and c.kind != 'STRING':
                self.putTokenBack()
                break

            if c.lineStart and tokensConsumed > 1:
                self.putTokenBack()
                break

            # This should be the only PUNCT that can break an expression.
            if c.body == ':':
                self.putTokenBack()
                break

            if c.kind == 'STRING':
                stack.append(c.body)
                continue

            c = c.body

            if c == '(':
                stack.append('(')
                continue

            if c == ')':
                while stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()
                continue

            if c in constants:
                output.append(constants[c])
                continue

            if c not in operators:
                output.append(float(c))
                continue

            if len(stack) == 0:
                stack.append(c)
                continue

            while len(stack) > 0 and (operators[c][0] < operators[stack[-1]][0] or (operators[c][0] == operators[stack[-1]][0] and not operators[c][1])):
                output.append(stack.pop())

            stack.append(c)

        for c in reversed(stack):
            output.append(c)

        stack = []

        for x in output:
            if x not in operators:
                if type(x) is str:
                    stack.append(Expression('STRING', x))
                if type(x) is float:
                    stack.append(Expression('NUM', x))
                if type(x) is bool:
                    stack.append(Expression('BOOL', 'true' if x else 'false'))
                continue

            b = stack.pop()
            a = stack.pop()

            expression = Expression('BINOP', x)
            expression.addChild('left', a)
            expression.addChild('right', b)
            stack.append(expression)

        return stack[0]

    def parseExpression(self):
        return self.shuntingYard()

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

    def parseFunctionArgs(self):
        token = self.nextToken()
        if token.kind != 'IDENT': return []
        args = [token.body]

        while True:
            token = self.nextToken()
            if token.kind == 'PUNCT' and token.body == ',':
                self.expectKind('IDENT', 'Expected an identifier in argument list')
                token = self.getCurrentToken()
                args.append(token.body)
            else:
                self.putTokenBack()
                break

        return args

    def parseFunction(self):
        node = Node('FUNCTION')
        self.expectKind('IDENT', 'Expected an identifier')
        identifier = self.getCurrentToken()
        node.addChild('name', identifier.body)
        self.expectToken('PUNCT', '(', 'Expected a `(`')
        node.addChild('args', self.parseFunctionArgs())
        self.expectToken('PUNCT', ')', 'Expected a `)`')
        self.expectToken('PUNCT', ':', 'Expected a `:`')
        self.expectKind('INDENT', 'Expected an indent at start of function body')
        node.addChild('body', self.parseStatement())
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
        elif token.body == 'def':
            return self.parseFunction()
        elif token.kind == 'DEDENT':
            return self.parseStatement()
        else:
            self.putTokenBack()
            expression = self.parseExpression()
            node = Node('EXPR')
            node.addChild('expression', expression)
            return node

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
