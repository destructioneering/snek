from Statement import *
from Expression import *
from Value import *
from Object import *
from Garbage import GarbageCollector
from Scope import Scope
from ReturnException import ReturnException

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
                return expression.function(self.evalExpression(scope, expression.left),
                                           self.evalExpression(scope, expression.right))
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
            elif statement.otherwise != None:
                if isinstance(statement.otherwise, list):
                    for s in statement.otherwise:
                        self.evalStatement(scope, s)
                else:
                    self.evalStatement(scope, statement.otherwise)
        elif isinstance(statement, PrintStatement):
            self.evalExpression(scope, statement.expression).print()
        elif isinstance(statement, ReturnStatement):
            raise ReturnException(self.evalExpression(scope, statement.expression))
        elif isinstance(statement, ExpressionStatement):
            self.evalExpression(scope, statement.expression)
        elif isinstance(statement, AssignStatement):
            scope.setVariable(statement.identifier, self.evalExpression(scope, statement.expression))
        elif isinstance(statement, FunctionStatement):
            obj = FunctionObject(scope, statement.parameters, statement.body, self)
            functionValue = FunctionValue(self.garbageCollector.allocate(obj))
            scope.setVariable(statement.identifier, functionValue)
        elif isinstance(statement, ClassStatement):
            # + Add ClassConstructor value to scope.
            # + Points to a ClassConstructorObject.
            # + ClassConstructorObject contains a dictionary with
            #   method names to FunctionObjects.
            # + Constructing a class looks up the ClassConstructorObject
            #   and calls the constructor as a regular function, passing
            #   in a new ClassValue, which points to a new ClassObject.
            #   Then it adds all of the methods from the ClassConstructorObject
            #   to the ClassObject.
            # + "Member" syntax will have to be implemented.
            # + When a MemberExpression is evaluated it'll check to
            #   see if the member is a function and if it is it'll
            #   return a MethodValue that's just a function with its
            #   ClassObject.

            obj = FunctionObject(scope, statement.parameters, statement.body, self)
            functionValue = FunctionValue(self.garbageCollector.allocate(obj))
            scope.setVariable(statement.identifier, functionValue)
        else:
            print(f"Invalid statement {statement}")

    def eval(self, statement):
        self.evalStatement(self.globalScope, statement)
