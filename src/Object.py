from Value import *
from Scope import Scope
from ReturnException import ReturnException

class Object:
    def __init__(self, gc):
        self.referenceCount = 0
        self.gc = gc

class FunctionObject(Object):
    def __init__(self, gc, scope, parameters, body, evaluator):
        super().__init__(gc)
        self.scope = scope
        self.parameters = parameters
        self.body = body
        self.evaluator = evaluator

    def delete(self, gc):
        for statement in self.body:
            gc.delete(statement)

    def apply(self, arguments):
        if len(self.parameters) != len(arguments):
            print('Incorrect number of arguments supplied to function')
        newscope = Scope(self.gc, self.scope)
        for i in range(len(arguments)):
            newscope.setVariable(self.parameters[i], arguments[i])

        for statement in self.body:
            try:
                self.evaluator.evalStatement(newscope, statement)
            except ReturnException as e:
                return e.value

        return NoneValue()

# The only difference between this and FunctionObject is that a
# FunctionObject has a bunch of statements as a body and may or may
# not return a value. A LambdaObject has only an expression for the
# body and just returns that.
class LambdaObject(Object):
    def __init__(self, gc, scope, parameters, body, evaluator):
        super().__init__(gc)
        self.scope = scope
        self.parameters = parameters
        self.body = body
        self.evaluator = evaluator

    def delete(self, gc):
        for k, v in self.scope.variables:
            gc.delete(v)
        for statement in self.body:
            gc.delete(statement)

    def apply(self, arguments):
        if len(self.parameters) != len(arguments):
            print('Incorrect number of arguments supplied to function')
        newscope = Scope(self.gc, self.scope)
        for i in range(len(arguments)):
            newscope.setVariable(self.parameters[i], arguments[i])
        return self.evaluator.evalExpression(newscope, self.body)

class ClassConstructorObject(Object):
    def __init__(self, gc, scope):
        super().__init__(gc)
        self.scope = scope

class ClassObject(Object):
    def __init__(self, gc, scope):
        super().__init__(gc)
        self.scope = scope
