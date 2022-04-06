from Statement import *
from Expression import *
from Value import *
from Object import *
from Garbage import GarbageCollector
from Scope import Scope

class Evaluator:
    def __init__(self):
        self.globalScope = Scope(None)
        self.garbageCollector = GarbageCollector()

    def error(self, errorMessage):
        print(f"Runtime error: {errorMessage}")

    def evalExpression(self, scope, expression):
        if isinstance(expression, BooleanExpression):
            return BooleanValue(expression.boolean)
        elif isinstance(expression, StringExpression):
            return StringValue(expression.string)
        elif isinstance(expression, BinaryExpression):
            if expression.operator == '==':
                return BooleanValue(self.evalExpression(scope, expression.left).compareTo(self.evalExpression(scope, expression.right)))
            if expression.operator == '!=':
                return BooleanValue(not self.evalExpression(scope, expression.left).compareTo(self.evalExpression(scope, expression.right)))
            else:
                return NumberValue(expression.function(self.evalExpression(scope, expression.left).number,
                                                       self.evalExpression(scope, expression.right).number))
        elif isinstance(expression, NumberExpression):
            return NumberValue(expression.number)
        elif isinstance(expression, IdentifierExpression):
            return scope.getVariable(expression.identifier)
        elif isinstance(expression, FunctionCallExpression):
            function = scope.getVariable(expression.identifier.identifier)
            arguments = [self.evalExpression(scope, x) for x in expression.parameters]
            return self.garbageCollector.getObject(function.gcReference).apply(arguments)
        elif isinstance(expression, LambdaExpression):
            obj = LambdaObject(scope, expression.parameters, expression.body, self)
            lambdaValue = LambdaValue(self.garbageCollector.allocate(obj))
            return lambdaValue
        elif isinstance(expression, NoneExpression):
            return NoneValue()
        else:
            print(f"Invalid expression {expression}")

    def evalStatement(self, scope, statement):
        if isinstance(statement, IfStatement):
            if self.evalExpression(scope, statement.condition).boolean == True:
                newscope = Scope(scope)
                for s in statement.body:
                    self.evalStatement(newscope, s)
        elif isinstance(statement, PrintStatement):
            self.evalExpression(scope, statement.expression).print()
        elif isinstance(statement, ExpressionStatement):
            self.evalExpression(scope, statement.expression)
        elif isinstance(statement, AssignStatement):
            scope.setVariable(statement.identifier, self.evalExpression(scope, statement.expression))
        elif isinstance(statement, FunctionStatement):
            obj = FunctionObject(scope, statement.parameters, statement.body, self)
            functionValue = FunctionValue(self.garbageCollector.allocate(obj))
            scope.setVariable(statement.identifier, functionValue)
        else:
            print(f"Invalid statement {statement}")

    def eval(self, statement):
        self.evalStatement(self.globalScope, statement)
