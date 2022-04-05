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
            ('(', ')', 7, 'left',  'member' ),
            ('[', ']', 7, 'left',  'member' ),
            ('+', 'n', 6, 'right', 'prefix', lambda a: a),
            ('-', 'n', 6, 'right', 'prefix', lambda a: -a ),
            ('(', ')', 6, 'left',  'group ' ),
            ('*', 'n', 5, 'left',  'binary', lambda a, b: a * b ),
            ('/', 'n', 5, 'left',  'binary', lambda a, b: a / b ),
            ('%', 'n', 5, 'left',  'binary', lambda a, b: a % b ),
            ('+', 'n', 4, 'left',  'binary', lambda a, b: a + b ),
            ('-', 'n', 4, 'left',  'binary', lambda a, b: a - b ),
            ('?', ':', 3, 'left',  'ternary', lambda a, b, c: b if a else c ),
        ]

    def nextToken(self):
        self.tokenIndex += 1

    def token(self):
        return self.tokens[self.tokenIndex] if self.tokenIndex < len(self.tokens) else Token('NONE', '', 0)

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

    def getPrecedence(self, precedence):
        operator = self.getInfixOp()
        return operator[2] if operator else precedence

    def parse(self, precedence=0):
        operator = self.getPrefixOp()
        left = None

        if operator:            # A prefix operator.
            if operator[4] == 'group':
                leftleft = self.parse()
                self.nextToken()
            else:
                leftleft = parse(operator[2])
            left = UnaryExpression(leftleft, operator[5])
        else:
            # No prefix operator, just parse a primary.
            if self.token().ident() != None:
                left = IdentifierExpression(self.token().ident())
                self.nextToken()
            elif self.token().num() != None:
                left = NumberExpression(self.token().num())
                self.nextToken()

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
                b = self.parse()
                if self.token().punct() != operator[1]:
                    print(f"Expression error: expected a {operator[1]}")
                self.nextToken()
                expression = MemberExpression(left, b)
            elif operator[4] == 'binary':
                self.nextToken()
                b = self.parse(operator[2] if operator[3] == 'left' else operator[2] - 1)
                expression = BinaryExpression(left, b, operator[5])
            elif operator[4] == 'postfix':
                self.nextToken()

            left = expression

        return expression
