class Expression:
    pass

class IdentifierExpression(Expression):
    def __init__(self, identifier):
        self.identifier = identifier

class BooleanExpression(Expression):
    def __init__(self, boolean):
        self.boolean = boolean

class StringExpression(Expression):
    def __init__(self, string):
        self.string = string

class NumberExpression(Expression):
    def __init__(self, number):
        self.number = number

class BinaryExpression(Expression):
    def __init__(self, left, right, function):
        self.left = left
        self.right = right
        self.function = function

class TernaryExpression(Expression):
    def __init__(self, a, b, c, function):
        self.a = a
        self.b = b
        self.c = c
        self.function = function

class MemberExpression(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right
