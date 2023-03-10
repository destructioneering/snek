class Expression:
    def __init__(self, operator):
        self.operator = operator

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

class FunctionCallExpression(Expression):
    def __init__(self, left, parameters):
        self.left = left
        self.parameters = parameters

class LambdaExpression(Expression):
    def __init__(self, parameters, body):
        self.parameters = parameters
        self.body = body

class NoneExpression(Expression):
    pass
