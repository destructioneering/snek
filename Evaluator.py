class Evaluator:
    def __init__(self, parser):
        self.parser = parser
        self.mathOps = {
            '^': lambda a, b: a ** b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b,
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            }
        self.globalScope = {}

    def error(self, errorMessage):
        print(f"Runtime error: {errorMessage}")

    def setVariable(self, scope, name, value):
        """
        Assign a variable in the current scope.
        """
        scope[name] = value

    def getVariable(self, scope, name):
        """
        Look up a variable in the current scope.
        """
        if name in scope: return scope[name]
        if name in self.globalScope: return self.globalScope[name]
        self.error(f"Undeclared variable {name}")

    def evalExpression(self, scope, expression):
        if expression.kind == 'BOOL':
            return expression.body == 'true'
        if expression.kind == 'STRING':
            return expression.body[1:-1]
        if expression.kind == 'BINOP':
            return self.mathOps[expression.body](self.evalExpression(scope, expression.children['left']),
                                                 self.evalExpression(scope, expression.children['right']))
        if expression.kind == 'NUM':
            return expression.body
        if expression.kind == 'IDENT':
            return self.getVariable(scope, expression.body)

    def evalStatement(self, scope, statement):
        if statement.kind == 'IF':
            if self.evalExpression(scope, statement.children['condition']):
                self.evalStatement(scope.copy(), statement.children['body'])
        elif statement.kind == 'PRINT':
            print(f"{self.evalExpression(scope, statement.children['expression'])}")
        elif statement.kind == 'EXPR':
            self.evalExpression(scope, statement.children['expression'])
        elif statement.kind == 'ASSIGN':
            self.setVariable(scope,
                             statement.children['variable'],
                             self.evalExpression(scope, statement.children['expression']))

    def eval(self):
        for statement in self.parser.statements:
            self.evalStatement(self.globalScope, statement)
