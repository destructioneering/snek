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

    def setVariable(self, scopes, name, value):
        """
        Assign a variable in the current scope.
        """
        if len(scopes) == 0:
            self.globalScope[name] = value
            return
        scopes[-1][name] = value

    def getVariable(self, scopes, name):
        """
        Look up a variable in the current scope.
        """
        for scope in reversed(scopes):
            if name in scope:
                return scope[name]
        if name in self.globalScope:
            return self.globalScope[name]
        self.error(f"Undeclared variable {name}")

    def evalExpression(self, scopes, expression):
        if expression.kind == 'BOOL':
            return expression.body == 'true'
        if expression.kind == 'STRING':
            return expression.body[1:-1]
        if expression.kind == 'BINOP':
            return self.mathOps[expression.body](self.evalExpression(scopes, expression.children['left']),
                                                 self.evalExpression(scopes, expression.children['right']))
        if expression.kind == 'NUM':
            return expression.body
        if expression.kind == 'IDENT':
            return self.getVariable(scopes, expression.body)

    def evalStatement(self, scopes, statement):
        if statement.kind == 'IF':
            if self.evalExpression(scopes, statement.children['condition']):
                self.evalStatement(scopes, statement.children['body'])
        elif statement.kind == 'PRINT':
            print(f"{self.evalExpression(scopes, statement.children['expression'])}")
        elif statement.kind == 'EXPR':
            self.evalExpression(scopes, statement.children['expression'])
        elif statement.kind == 'ASSIGN':
            self.setVariable(scopes,
                             statement.children['variable'],
                             self.evalExpression(scopes, statement.children['expression']))

    def eval(self):
        blankScope = []
        for statement in self.parser.statements:
            self.evalStatement(blankScope, statement)
