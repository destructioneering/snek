from Expression import *
from Token import Token
from Value import *

class ExpressionParser:
    """
    A Pratt parser.
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.tokenIndex = 0
        self.operators = [
            ('.', 'n', 9, 'left',  'binary', lambda a, b: None ),
            ('(', ')', 8, 'left',  'member' ),
            ('[', ']', 8, 'left',  'member' ),
            ('+', 'n', 7, 'right', 'prefix',  lambda a: a),
            ('-', 'n', 7, 'right', 'prefix',  lambda a: -NumberValue(a.number) ),
            ('(', ')', 7, 'left',  'group'  ),
            ('**', 'n', 6, 'left',  'binary', lambda a, b: NumberValue(a.number ** b.number) ),
            ('*', 'n', 5, 'left',  'binary',  lambda a, b: NumberValue(a.number * b.number) ),
            ('/', 'n', 5, 'left',  'binary',  lambda a, b: NumberValue(a.number / b.number) ),
            ('%', 'n', 5, 'left',  'binary',  lambda a, b: NumberValue(a.number % b.number) ),
            ('+', 'n', 4, 'left',  'binary',  lambda a, b: NumberValue(a.number + b.number) ),
            ('-', 'n', 4, 'left',  'binary',  lambda a, b: NumberValue(a.number - b.number) ),
            ('==', 'n', 3, 'left',  'binary', lambda a, b: None ),
            ('!=', 'n', 3, 'left',  'binary', lambda a, b: None ),
            ('<=', 'n', 3, 'left',  'binary', lambda a, b: BooleanValue(a.number <= b.number) ),
            ('>=', 'n', 3, 'left',  'binary', lambda a, b: BooleanValue(a.number >= b.number) ),
            ('<', 'n', 3, 'left',  'binary',  lambda a, b: BooleanValue(a.number < b.number) ),
            ('>', 'n', 3, 'left',  'binary',  lambda a, b: BooleanValue(a.number > b.number) ),
            ('=', 'n', 2, 'right',  'binary', lambda a, b: None ),
            ('if', 'else', 1, 'left',  'ternary', lambda a, b, c: b if a else c ),
        ]

    def expect(self, condition, errorString):
        if not condition:
            self.error(errorString)

    def putTokenBack(self):
        self.tokenIndex -= 1
        return self.tokens[self.tokenIndex]

    def nextToken(self):
        self.tokenIndex += 1
        if self.tokenIndex >= len(self.tokens): return None
        return self.tokens[self.tokenIndex - 1]

    def token(self):
        return self.tokens[self.tokenIndex] if self.tokenIndex < len(self.tokens) else Token('NONE', '', False)

    def getInfixOp(self):
        for operator in self.operators:
            if self.token().punct() == operator[0] and operator[4] != 'prefix':
                return operator
        return None

    def getPrefixOp(self):
        for operator in self.operators:
            if self.token().punct() == operator[0] and (operator[4] == 'prefix' or operator[4] == 'group'):
                return operator
        return None

    def parseFunctionParameters(self):
        if self.token().punct() == ')': return []
        parameters = [self.parse()]

        while True:
            if self.token().punct() == ',':
                self.nextToken()
                parameters.append(self.parse())
            else:
                break

        return parameters

    def getPrecedence(self, precedence):
        operator = self.getInfixOp()
        return operator[2] if operator else precedence

    def parse(self, precedence=0):
        operator = self.getPrefixOp()
        left = None

        if operator:            # A prefix operator.
            if operator[4] == 'group':
                self.nextToken()
                left = self.parse()
                self.nextToken() # Skip over the )
            else:
                self.nextToken()
                leftleft = self.parse(operator[2])
                left = UnaryExpression(operator[0], leftleft, operator[5])
        else:
            # No prefix operator, just parse a primary.
            if self.token().ident() != None:
                if self.token().ident() == 'None':
                    left = NoneExpression('None')
                    self.nextToken()
                elif self.token().ident() == 'lambda':
                    self.nextToken()
                    parameters = [x.identifier for x in self.parseFunctionParameters()]
                    self.expect(self.token().punct() == ':', 'Expected a `:`')
                    self.nextToken()
                    body = self.parse()
                    left = LambdaExpression(parameters, body)
                else:
                    left = IdentifierExpression(self.token().ident())
                    self.nextToken()
            elif self.token().num() != None:
                left = NumberExpression(self.token().num())
                self.nextToken()
            elif self.token().string() != None:
                left = StringExpression(self.token().string()[1:-1])
                self.nextToken()
            elif self.token().bool() != None:
                left = BooleanExpression(self.token().bool())
                self.nextToken()
            else:
                print(f"Expression error: unrecognized primary ({self.token().print()})")
                abort()

        operator = self.getInfixOp()
        expression = left

        while precedence < self.getPrecedence(precedence):
            operator = self.getInfixOp()
            if operator == None: return left

            if operator[4] == 'ternary':
                self.nextToken()
                b = self.parse(1)
                if self.token().punct() != operator[1]:
                    print(f"Expression error: expected a {operator[1]}")
                self.nextToken()
                c = self.parse(1)
                expression = TernaryOperator(left, b, c, operator[5])
            elif operator[4] == 'member':
                self.nextToken()
                if operator[0] == '(': # Function call
                    parameters = self.parseFunctionParameters()
                    if self.token().punct() != operator[1]:
                        print(f"Expression error: expected a {operator[1]} (got {self.token().punct()})")
                    self.nextToken()
                    expression = FunctionCallExpression(left, parameters)
                else:
                    b = self.parse()
                    if self.token().punct() != operator[1]:
                        print(f"Expression error: expected a {operator[1]} (got {self.token().punct()})")
                    self.nextToken()
                    expression = MemberExpression(operator[0], left, b)
            elif operator[4] == 'binary':
                self.nextToken()
                b = self.parse(operator[2] if operator[3] == 'left' else operator[2] - 1)
                expression = BinaryExpression(operator[0], left, b, operator[5])
            elif operator[4] == 'postfix':
                self.nextToken()

            left = expression

            if self.token().lineStart:
                break

        return expression
