from Statement import *
from Expression import *
from Value import *
from Object import *
from Garbage import GarbageCollector
from Scope import Scope
from ReturnException import ReturnException

def printBuiltin(args):
    for arg in args:
        arg.print()
    print()

class Evaluator:
    def __init__(self):
        self.gc = GarbageCollector()
        self.globalScope = Scope(self.gc, None)
        self.globalScope.setVariable('print', BuiltinValue(printBuiltin))

    def cleanUp(self):
        self.globalScope.delete()

    def error(self, errorMessage):
        print(f"Runtime error: {errorMessage}")

    def getScopeFromExpression(self, scope, expression):
        if isinstance(expression, BinaryExpression) and expression.operator == '.':
            left = self.getScopeFromExpression(scope, expression.left)
            right = self.evalExpression(left, expression.right)
            return self.gc.getObject(right.gcReference).scope
        else:
            if isinstance(expression, IdentifierExpression):
                val = scope.getVariable(expression.identifier)
                return self.gc.getObject(val.gcReference).scope
            else:
                print('error')

    def evalExpression(self, scope, expression):
        if isinstance(expression, BooleanExpression):
            return BooleanValue(expression.boolean)
        elif isinstance(expression, StringExpression):
            return StringValue(expression.string)
        elif isinstance(expression, BinaryExpression):
            if expression.operator == '==':
                return BooleanValue(self.evalExpression(scope, expression.left).compareTo(self.evalExpression(scope, expression.right)))
            elif expression.operator in ['=', '*=', '+=', '-=', '/=']:
                if isinstance(expression.left, BinaryExpression):
                    # The lefthand side of the = should be a x.y type thing.
                    newscope = self.getScopeFromExpression(scope, expression.left.left)
                    lefthand = None
                    try:
                        lefthand = self.evalExpression(scope, expression.left)
                    except:     # TODO: Make a custom exception for undeclared variables.
                        # TODO: Assert that this is a = and not a += or something like that.
                        lefthand = None
                    righthand = self.evalExpression(scope, expression.right)
                    val = expression.function(lefthand, righthand)
                    newscope.setVariable(expression.left.right.identifier, val)
                    return val
                else:
                    # The lefthand side of the = should be an identifier then.
                    lefthand = None
                    try:
                        lefthand = self.evalExpression(scope, expression.left)
                    except:
                        lefthand = None
                    righthand = self.evalExpression(scope, expression.right)
                    val = expression.function(lefthand, righthand)
                    scope.setVariable(expression.left.identifier, val)
                    return val
            elif expression.operator == '!=':
                return BooleanValue(not self.evalExpression(scope, expression.left).compareTo(self.evalExpression(scope, expression.right)))
            elif expression.operator == '.':
                left = self.evalExpression(scope, expression.left)
                if not isinstance(left, ClassValue): print('error')
                identifier = expression.right.identifier
                classObject = self.gc.getObject(left.gcReference)
                right = classObject.scope.getVariable(identifier)
                if isinstance(right, FunctionValue):
                    return MethodValue(left, right.gcReference)
                else:
                    return right
            else:
                return expression.function(self.evalExpression(scope, expression.left),
                                           self.evalExpression(scope, expression.right))
        elif isinstance(expression, NumberExpression):
            return NumberValue(expression.number)
        elif isinstance(expression, IdentifierExpression):
            return scope.getVariable(expression.identifier)
        elif isinstance(expression, FunctionCallExpression):
            function = self.evalExpression(scope, expression.left)
            if isinstance(function, ClassConstructorValue):
                newscope = self.gc.getObject(function.gcReference).scope.copy()
                obj = ClassObject(self.gc, newscope)
                val = ClassValue(self.gc, self.gc.allocate(obj))
                scope.addObject(val.gcReference)
                if '__init__' in newscope.variables:
                    constructor = newscope.variables['__init__']
                    arguments = [self.evalExpression(scope, x) for x in expression.parameters]
                    self.gc.getObject(constructor.gcReference).apply([val] + arguments)
                return val
            elif isinstance(function, MethodValue):
                classValue = function.classValue
                arguments = [self.evalExpression(scope, x) for x in expression.parameters]
                return self.gc.getObject(function.gcReference).apply([classValue] + arguments)
            elif isinstance(function, FunctionValue) or isinstance(function, LambdaValue):
                arguments = [self.evalExpression(scope, x) for x in expression.parameters]
                return self.gc.getObject(function.gcReference).apply(arguments)
            elif isinstance(function, BuiltinValue):
                arguments = [self.evalExpression(scope, x) for x in expression.parameters]
                return function.function(arguments)
            else:
                print(f"error: {function}")
        elif isinstance(expression, LambdaExpression):
            obj = LambdaObject(self.gc, scope, expression.parameters, expression.body, self)
            lambdaValue = LambdaValue(self.gc.allocate(obj))
            scope.addObject(lambdaValue.gcReference)
            return lambdaValue
        elif isinstance(expression, NoneExpression):
            return NoneValue()
        else:
            print(f"Invalid expression {expression}")

    def evalStatement(self, scope, statement):
        if isinstance(statement, IfStatement):
            if self.evalExpression(scope, statement.condition).boolean == True:
                newscope = Scope(self.gc, scope)
                for s in statement.body:
                    self.evalStatement(newscope, s)
                newscope.delete()
            elif statement.otherwise != None:
                if isinstance(statement.otherwise, list):
                    for s in statement.otherwise:
                        self.evalStatement(scope, s)
                else:
                    self.evalStatement(scope, statement.otherwise)
        elif isinstance(statement, WhileStatement):
            while self.evalExpression(scope, statement.condition).boolean == True:
                newscope = Scope(self.gc, scope)
                for s in statement.body:
                    self.evalStatement(newscope, s)
                newscope.delete()
        elif isinstance(statement, PrintStatement):
            self.evalExpression(scope, statement.expression).print()
        elif isinstance(statement, ReturnStatement):
            raise ReturnException(self.evalExpression(scope, statement.expression))
        elif isinstance(statement, ExpressionStatement):
            self.evalExpression(scope, statement.expression)
        elif isinstance(statement, FunctionStatement):
            obj = FunctionObject(self.gc, scope, statement.parameters, statement.body, self)
            functionValue = FunctionValue(self.gc.allocate(obj))
            scope.setVariable(statement.identifier, functionValue)
        elif isinstance(statement, ClassStatement):
            newscope = Scope(self.gc, scope)
            for stmt in statement.body:
                self.evalStatement(newscope, stmt)
            obj = ClassConstructorObject(self.gc, newscope)
            val = ClassConstructorValue(self.gc.allocate(obj))
            scope.setVariable(statement.identifier, val)
        else:
            print(f"Invalid statement {statement}")

    def eval(self, statement):
        self.evalStatement(self.globalScope, statement)
