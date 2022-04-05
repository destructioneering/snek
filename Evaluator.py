class Evaluator:
    def __init__(self, parser):
        self.parser = parser

    def evalExpression(self, expression):
        if expression.kind == 'BOOL':
            return expression.body == 'true'
        if expression.kind == 'STRING':
            return expression.body[1:-1]

    def evalStatement(self, statement):
        if statement.kind == 'IF':
            if self.evalExpression(statement.children['condition']):
                self.evalStatement(statement.children['body'])
        elif statement.kind == 'PRINT':
            print(f"{self.evalExpression(statement.children['expression'])}")

    def eval(self):
        for statement in self.parser.statements:
            self.evalStatement(statement)
