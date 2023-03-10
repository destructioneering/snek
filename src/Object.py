import logging, uuid, random, string

from Value import *
from ReturnException import ReturnException

class Object:
    def __init__(self, gc):
        self.gc = gc

        # Reference counter
        self.referenceCount = 0

        # Tracer
        self.color = 0

        self.colors = ['white', 'pink', 'purple']

    def markvisited(self):
        if self.color > 1: return
        self.color = 1
        if self.gc.hide_functions and isinstance(self, FunctionObject): return
        if self.gc.hide_scopes and self.idx != 0 and isinstance(self, ScopeObject): return
        color = self.colors[self.color]
        self.gc.evaluator.events[-1]['frames'][-1] += f"{self.idx} [fillcolor={color}];\n";

    def markalive(self):
        self.color = 2
        if self.gc.hide_functions and isinstance(self, FunctionObject): return
        if self.gc.hide_scopes and self.idx != 0 and isinstance(self, ScopeObject): return
        color = self.colors[self.color]
        self.gc.evaluator.events[-1]['frames'][-1] += f"{self.idx} [fillcolor={color}];\n";

    def render_graph(self):
        if not self.alive(): return ''
        result = f"{self.idx} [label=\"{type(self).__name__[0:-6]}[{self.idx}]\\nreferences: {self.referenceCount}\", style=filled];\n"
        return result

    def alive(self):
        return (not self.gc.hide_dead) or self.referenceCount > 0

class FunctionObject(Object):
    def __init__(self, gc, scope, parameters, body, evaluator):
        super().__init__(gc)
        # Can't copy the scope because variables assigned to the
        # enclosing in the future wouldn't be accessible inside the
        # function.
        self.scope = ScopeValue(gc, gc.allocate(ScopeObject(gc, scope, self)))
        self.gc.addReference(self.scope)
        self.parameters = parameters
        self.body = body
        self.evaluator = evaluator

    def render_graph(self):
        if not self.alive(): return ''
        result = super().render_graph()
        if not self.gc.hide_scopes and self.scope.scope.alive(): result += f"{self.idx} -> {self.scope.scope.idx} [label=\"<SCOPE>\"];\n"
        return result

    def trace(self):
        if self.color > 1: return
        self.markalive()
        self.scope.scope.trace()

    def subReference(self):
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

        newscope = ScopeValue(self.gc, self.gc.allocate(ScopeObject(self.gc, self.scope, self)))
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
        # Can't copy the scope because variables assigned to the
        # enclosing in the future wouldn't be accessible inside the
        # function.
        self.scope = ScopeValue(gc, gc.allocate(ScopeObject(gc, scope, self)))
        self.gc.addReference(self.scope)
        self.parameters = parameters
        self.body = body
        self.evaluator = evaluator

    def render_graph(self):
        if not self.alive(): return ''
        result = super().render_graph()
        if not self.gc.hide_scopes and self.scope.scope.alive(): result += f"{self.idx} -> {self.scope.scope.idx} [label=\"<SCOPE>\"];\n"
        return result

    def trace(self):
        if self.color > 1: return
        self.markalive()
        self.scope.scope.trace()

    def subReference(self):
        self.gc.subReference(self.scope)

    # def apply(self, arguments):
    #     if len(self.parameters) != len(arguments):
    #         print('Incorrect number of arguments supplied to lambda')
    #     return self.evaluator.evalExpression(self.scope, self.body)

    def apply(self, arguments):
        logging.debug('Lambda application %s', self)

        if len(self.parameters) != len(arguments):
            print('Incorrect number of arguments supplied to function')

        newscope = ScopeValue(self.gc, self.gc.allocate(ScopeObject(self.gc, self.scope, self)))
        self.gc.addReference(newscope)

        for i in range(len(arguments)):
            newscope.setVariable(self.parameters[i], arguments[i])

        val = self.evaluator.evalExpression(newscope, self.body)
        self.gc.subReference(newscope)

        return val

class ClassConstructorObject(Object):
    def __init__(self, gc, scope):
        super().__init__(gc)
        self.scope = ScopeValue(gc, gc.allocate(ScopeObject(gc, scope, self)))
        self.gc.addReference(self.scope)

    def render_graph(self):
        if not self.alive(): return ''
        result = super().render_graph()
        if not self.gc.hide_scopes and self.scope.scope.alive(): result += f"{self.idx} -> {self.scope.scope.idx} [label=\"<SCOPE>\"];\n"
        return result

    def trace(self):
        if self.color > 1: return
        self.markalive()
        self.scope.scope.trace()

    def subReference(self):
        self.gc.subReference(self.scope)

class ClassObject(Object):
    def __init__(self, gc, scope):
        super().__init__(gc)
        self.scope = scope
        self.gc.addReference(self.scope)

    def render_graph(self):
        if not self.alive(): return ''
        result = super().render_graph()
        if not self.gc.hide_scopes and self.scope.scope.alive(): result += f"{self.idx} -> {self.scope.scope.idx} [label=\"<SCOPE>\"];\n"
        return result

    def trace(self):
        if self.color > 1: return
        self.markalive()
        self.scope.scope.trace()

    def subReference(self):
        self.gc.subReference(self.scope)

class ScopeObject(Object):
    def __init__(self, gc, parent, owner):
        # Parent should be a ScopeValue.
        super().__init__(gc)
        self.parent = None
        self.owner = owner
        if isinstance(parent, Object):
            abort()
        if parent:
            self.gc.addReference(parent)
            self.parent = self.gc.getObject(parent.gcReference)
        self.variables = {}
        self.registers = []

    def trace(self):
        if self.color > 1: return
        self.markalive()

        for identifier, value in self.variables.items():
            if isinstance(value, ReferenceValue):
                self.gc.getObject(value.gcReference).markvisited()

        if self.owner:
            if self.gc.hide_functions and isinstance(self.owner, FunctionObject):
                pass
            else:
                self.gc.new_frame()
        else:
            self.gc.new_frame()

        if self.parent:
            self.parent.trace()

        for identifier, value in self.variables.items():
            if isinstance(value, ReferenceValue):
                self.gc.getObject(value.gcReference).trace()

    def render_graph(self):
        if not self.alive(): return ''

        result = ''
        host = self.idx

        if self.gc.hide_scopes and self.owner:
            host = self.owner.idx
        elif not self.gc.hide_scopes:
            result += super().render_graph()

        if self.gc.hide_functions and isinstance(self.owner, FunctionObject): return ''

        if not self.gc.hide_parents and self.parent:
            if self.gc.hide_scopes:
                if self.parent.owner:
                    result += f"{host} -> {self.parent.owner.idx};"
                elif self.parent.idx == 0:
                    result += f"{host} -> {self.parent.idx};"
            else:
                result += f"{host} -> {self.parent.idx};"

        for identifier, value in self.variables.items():
            if self.gc.hide_functions and isinstance(value, FunctionValue): continue
            if isinstance(value, ReferenceValue):
                result += f"{host} -> {value.gcReference} [label=\"{identifier}\"];\n"
            elif not isinstance(value, BuiltinValue):
                fakename = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=5))
                result += f"{fakename} [label=\"{value.render_graph()}\"];\n"
                result += f"{host} -> {fakename} [label=\"{identifier}\"];\n"

        # for idx, value in enumerate(self.registers):
        #     if not isinstance(value, ReferenceValue): continue
        #     result += f"{host} -> {value.gcReference} [label=\"register[{idx}]\"];\n"

        return result

    def setVariable(self, identifier, value):
        oldValue = self.getVariable(identifier)

        # When a variable is set to an object then the object
        # shouldn't die while that variable is referencing it.
        self.gc.addReference(value)

        if oldValue != None:
            #print(f"Variable re-assignment: {identifier}")
            self.gc.subReference(oldValue)

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

        scope = ScopeValue(self.gc, self.gc.allocate(ScopeObject(self.gc, parent, parent.scope.owner)))

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

    def subReference(self):
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
