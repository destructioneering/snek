from Expression import *
from Token import Token

class ExpressionParser:
    """
    A Pratt parser.
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.tokenIndex = 0
        self.operators = [
            ('(', ')', 8, 'left',  'member' ),
            ('[', ']', 8, 'left',  'member' ),
            ('+', 'n', 7, 'right', 'prefix', lambda a: a),
            ('-', 'n', 7, 'right', 'prefix', lambda a: -a ),
            ('(', ')', 7, 'left',  'group'  ),
            ('**', 'n', 6, 'left',  'binary', lambda a, b: a ** b ),
            ('*', 'n', 5, 'left',  'binary', lambda a, b: a * b ),
            ('/', 'n', 5, 'left',  'binary', lambda a, b: a / b ),
            ('%', 'n', 5, 'left',  'binary', lambda a, b: a % b ),
            ('+', 'n', 4, 'left',  'binary', lambda a, b: a + b ),
            ('-', 'n', 4, 'left',  'binary', lambda a, b: a - b ),
            ('?', ':', 3, 'left',  'ternary', lambda a, b, c: b if a else c ),
        ]

    def putTokenBack(self):
        self.tokenIndex -= 1
        return self.tokens[self.tokenIndex]

    def nextToken(self):
        if self.tokenIndex >= len(self.tokens): return None
        self.tokenIndex += 1
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
                print(f"Expression error: unrecognized primary ({self.token().body})")
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
