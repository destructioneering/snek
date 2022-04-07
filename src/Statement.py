class Statement:
    pass

class IfStatement(Statement):
    def __init__(self, condition, body, otherwise):
        self.condition = condition
        self.body = body
        self.otherwise = otherwise

class PrintStatement(Statement):
    def __init__(self, expression):
        self.expression = expression

class ReturnStatement(Statement):
    def __init__(self, expression):
        self.expression = expression

class ExpressionStatement(Statement):
    def __init__(self, expression):
        self.expression = expression

class AssignStatement(Statement):
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression

class FunctionStatement(Statement):
    def __init__(self, identifier, parameters, body):
        self.identifier = identifier
        self.parameters = parameters
        self.body = body

class ClassStatement(Statement):
    def __init__(self, identifier, methods):
        self.identifier = identifier
        self.methods = methods
