from Statement import *
from Expression import *
from Value import *
from Object import *
from Garbage import GarbageCollector

class Evaluator:
    def __init__(self):
        self.globalScope = {}
        self.garbageCollector = GarbageCollector()

    def error(self, errorMessage):
        print(f"Runtime error: {errorMessage}")

    def setVariable(self, scope, identifier, value):
        scope[identifier] = value

    def getVariable(self, scope, identifier):
        if identifier in scope: return scope[identifier]
        if identifier in self.globalScope: return self.globalScope[identifier]
        self.error(f"Undeclared variable {identifier}")

    def evalExpression(self, scope, expression):
        if isinstance(expression, BooleanExpression):
            return BooleanValue(expression.boolean)
        elif isinstance(expression, StringExpression):
            return StringValue(expression.string)
        elif isinstance(expression, BinaryExpression):
            return NumberValue(expression.function(self.evalExpression(scope, expression.left).number,
                                                   self.evalExpression(scope, expression.right).number))
        elif isinstance(expression, NumberExpression):
            return NumberValue(expression.number)
        elif isinstance(expression, IdentifierExpression):
            return self.getVariable(scope, expression.identifier)
        elif isinstance(expression, FunctionCallExpression):
            function = self.getVariable(scope, expression.identifier.identifier)
            arguments = [self.evalExpression(scope, x) for x in expression.parameters]
            return self.garbageCollector.getObject(function.gcReference).apply(arguments)

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
        elif isinstance(statement, FunctionStatement):
            obj = FunctionObject(scope, statement.parameters, statement.body, self)
            functionValue = FunctionValue(self.garbageCollector.allocate(obj))
            self.setVariable(scope, statement.identifier, functionValue)

    def eval(self, statement):
        self.evalStatement(self.globalScope, statement)
