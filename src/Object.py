import logging

from Value import *
from ReturnException import ReturnException

class Object:
    def __init__(self, gc):
        self.gc = gc

        # Reference counter
        self.referenceCount = 0

class FunctionObject(Object):
    def __init__(self, gc, scope, parameters, body, evaluator):
        super().__init__(gc)
        # Can't copy the scope because variables assigned to the
        # enclosing in the future wouldn't be accessible inside the
        # function.
        self.scope = ScopeValue(gc, gc.allocate(ScopeObject(gc, scope)))
        self.gc.addReference(self.scope)
        self.parameters = parameters
        self.body = body
        self.evaluator = evaluator

    def delete(self):
        # We don't need to delete the scope because the scope wasn't
        # copied. This function will only live until its outer scope
        # dies unless there are other references to it... Actually, I
        # think we do need to delete the scope:
        #
        # x = None
        # def ():
        #     y = 2
        #     def g():
        #         return y
        #     x = g
        # print(x())
        #
        # So basically all functions are lambdas now. In the global
        # scope there's no difference because the global scope won't
        # die until the program is over.
        self.gc.subReference(self.scope)

    def apply(self, arguments):
        logging.debug('Function application %s', self)

        if len(self.parameters) != len(arguments):
            print('Incorrect number of arguments supplied to function')

        newscope = ScopeValue(self.gc, self.gc.allocate(ScopeObject(self.gc, self.scope)))
        self.gc.addReference(newscope)

        for i in range(len(arguments)):
            newscope.setVariable(self.parameters[i], arguments[i])

        for statement in self.body:
            try:
                self.evaluator.evalStatement(newscope, statement)
            except ReturnException as e:
                self.gc.subReference(newscope)
                return e.value

        self.gc.subReference(newscope)

        return NoneValue()

# The only difference between this and FunctionObject is that a
# FunctionObject has a bunch of statements as a body and may or may
# not return a value. A LambdaObject has only an expression for the
# body and just returns that.
class LambdaObject(Object):
    def __init__(self, gc, scope, parameters, body, evaluator):
        super().__init__(gc)
        self.scope = scope.copy()
        # print(self.scope.scope.variables)
        self.gc.addReference(self.scope)
        logging.debug(gc.objects[self.scope.gcReference].referenceCount)
        self.parameters = parameters
        self.body = body
        self.evaluator = evaluator

    def delete(self):
        self.gc.subReference(self.scope)

    # def apply(self, arguments):
    #     if len(self.parameters) != len(arguments):
    #         print('Incorrect number of arguments supplied to lambda')
    #     return self.evaluator.evalExpression(self.scope, self.body)

    def apply(self, arguments):
        logging.debug('Lambda application %s', self)

        if len(self.parameters) != len(arguments):
            print('Incorrect number of arguments supplied to function')

        newscope = ScopeValue(self.gc, self.gc.allocate(ScopeObject(self.gc, self.scope)))
        self.gc.addReference(newscope)

        for i in range(len(arguments)):
            newscope.setVariable(self.parameters[i], arguments[i])

        val = self.evaluator.evalExpression(newscope, self.body)
        self.gc.subReference(newscope)
        return val

class ClassConstructorObject(Object):
    def __init__(self, gc, scope):
        super().__init__(gc)
        self.scope = scope

    def delete(self):
        self.gc.subReference(self.scope)

class ClassObject(Object):
    def __init__(self, gc, scope):
        super().__init__(gc)
        self.scope = scope

    def delete(self):
        self.gc.subReference(self.scope)

class ScopeObject(Object):
    def __init__(self, gc, parent):
        # Parent should be a ScopeValue.
        super().__init__(gc)
        self.parent = None
        if isinstance(parent, Object):
            abort()
        if parent:
            self.gc.addReference(parent)
            self.parent = self.gc.getObject(parent.gcReference)
        self.variables = {}
        self.registers = []

    def setVariable(self, identifier, value):
        oldValue = self.getVariable(identifier)

        if oldValue != None:
            #print(f"Variable re-assignment: {identifier}")
            self.gc.subReference(oldValue)

        # When a variable is set to an object then the object
        # shouldn't die while that variable is referencing it.
        self.gc.addReference(value)

        scope = self

        # Walk up the linked list to see if the variable already
        # exists.
        while scope != None:
            if identifier in scope.variables:
                scope.variables[identifier] = value
                return
            scope = scope.parent

        # If the variable doesn't exist in any scope then it's a new
        # variable we should add to the current scope.
        self.variables[identifier] = value

    def getVariable(self, identifier):
        if identifier in self.variables:
            return self.variables[identifier]
        if self.parent != None:
            return self.parent.getVariable(identifier)
        return None

    def copy(self):
        parent = None

        if self.parent:
            parent = ScopeValue(self.gc, self.parent.idx)

        scope = ScopeValue(self.gc, self.gc.allocate(ScopeObject(self.gc, parent)))

        for variableName, variableValue in self.variables.items():
            # When the scope is copied (which is probably for a lambda
            # expression), it would be a shame if the objects in it
            # suddenly disappeared. A scope in that sense is kind of
            # an object itself. In any case, the objects have a new
            # reference in the new scope.
            scope.setVariable(variableName, variableValue)

        # The registers aren't copied because they contain information
        # that's only relevent to a specific scope and doesn't affect
        # evaluation.

        return scope

    def delete(self):
        self.clearRegisters()
        self.gc.subReference(self.parent)
        for variableName, variableValue in self.variables.items():
            self.gc.subReference(variableValue)

    def setRegister(self, value):
        if isinstance(value, ReferenceValue) or isinstance(value, Object):
            self.gc.addReference(value)
            self.registers.append(value)

    def clearRegisters(self):
        for value in self.registers:
            self.gc.subReference(value)
        self.registers = []
