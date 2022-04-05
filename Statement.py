class Statement:
    pass

class IfStatement(Statement):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class PrintStatement(Statement):
    def __init__(self, expression):
        self.expression = expression

class ExpressionStatement(Statement):
    def __init__(self, expression):
        self.expression = expression

class AssignStatement(Statement):
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression