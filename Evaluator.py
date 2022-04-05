from Statement import *
from Expression import *

class Evaluator:
    def __init__(self):
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
        if isinstance(expression, BooleanExpression):
            return expression.boolean
        if isinstance(expression, StringExpression):
            return expression.string
        if isinstance(expression, BinaryExpression):
            return expression.function(self.evalExpression(scope, expression.left),
                                       self.evalExpression(scope, expression.right))
        if isinstance(expression, NumberExpression):
            return expression.number
        if isinstance(expression, IdentifierExpression):
            return self.getVariable(scope, expression.identifier)

    def evalStatement(self, scope, statement):
        if isinstance(statement, IfStatement):
            if self.evalExpression(scope, statement.condition):
                self.evalStatement(scope.copy(), statement.body)
        elif isinstance(statement, PrintStatement):
            print(f"{self.evalExpression(scope, statement.expression)}")
        elif isinstance(statement, ExpressionStatement):
            self.evalExpression(scope, statement.expression)
        elif isinstance(statement, AssignStatement):
            self.setVariable(scope, statement.identifier, self.evalExpression(scope, statement.expression))

    def eval(self, statement):
        self.evalStatement(self.globalScope, statement)
