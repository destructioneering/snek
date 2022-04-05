from Statement import *
from Expression import *
from Value import *

class Evaluator:
    def __init__(self):
        self.globalScope = {}

    def error(self, errorMessage):
        print(f"Runtime error: {errorMessage}")

    def setVariable(self, scope, name, value):
        scope[name] = value

    def getVariable(self, scope, name):
        if name in scope: return scope[name]
        if name in self.globalScope: return self.globalScope[name]
        self.error(f"Undeclared variable {name}")

    def evalExpression(self, scope, expression):
        if isinstance(expression, BooleanExpression):
            return BooleanValue(expression.boolean)
        if isinstance(expression, StringExpression):
            return StringValue(expression.string)
        if isinstance(expression, BinaryExpression):
            return NumberValue(expression.function(self.evalExpression(scope, expression.left).number,
                                                   self.evalExpression(scope, expression.right).number))
        if isinstance(expression, NumberExpression):
            return NumberValue(expression.number)
        if isinstance(expression, IdentifierExpression):
            return self.getVariable(scope, expression.identifier)

    def evalStatement(self, scope, statement):
        if isinstance(statement, IfStatement):
            if self.evalExpression(scope, statement.condition):
                self.evalStatement(scope.copy(), statement.body)
        elif isinstance(statement, PrintStatement):
            self.evalExpression(scope, statement.expression).print()
        elif isinstance(statement, ExpressionStatement):
            self.evalExpression(scope, statement.expression)
        elif isinstance(statement, AssignStatement):
            self.setVariable(scope, statement.identifier, self.evalExpression(scope, statement.expression))

    def eval(self, statement):
        self.evalStatement(self.globalScope, statement)
