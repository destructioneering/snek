class Expression:
    def __init__(self, operator):
        self.operator = operator

class IdentifierExpression(Expression):
    def __init__(self, identifier):
        self.identifier = identifier

class BooleanExpression(Expression):
    def __init__(self, operator, boolean):
        super().__init__(operator)
        self.boolean = boolean

class StringExpression(Expression):
    def __init__(self, operator, string):
        super().__init__(operator)
        self.string = string

class NumberExpression(Expression):
    def __init__(self, number):
        self.number = number

class UnaryExpression(Expression):
    def __init__(self, operator, expression, function):
        super().__init__(operator)
        self.expression = expression
        self.function = function

class BinaryExpression(Expression):
    def __init__(self, operator, left, right, function):
        super().__init__(operator)
        self.left = left
        self.right = right
        self.function = function

class TernaryExpression(Expression):
    def __init__(self, operator, a, b, c, function):
        super().__init__(operator)
        self.a = a
        self.b = b
        self.c = c
        self.function = function

class MemberExpression(Expression):
    def __init__(self, operator, left, right):
        super().__init__(operator)
        self.left = left
        self.right = right
