class Value:
    def __init__(self, gc):
        self.gc = gc

class ReferenceValue(Value):
    def __init__(self, gc):
        super().__init__(gc)

    def compareTo(self, value):
        if not isinstance(value, ReferenceValue): return False
        return self.gcReference == value.gcReference

class StringValue(Value):
    def __init__(self, string):
        self.string = string

    def print(self):
        print(self.string, end="")

    def render_graph(self):
        return self.string

    def compareTo(self, value):
        if not isinstance(value, StringValue): return False
        return self.string == value.string

class NumberValue(Value):
    def __init__(self, number):
        self.number = number

    def print(self):
        print(self.number, end="")

    def render_graph(self):
        return str(self.number)

    def compareTo(self, value):
        if not isinstance(value, NumberValue): return False
        return self.number == value.number

class BooleanValue(Value):
    def __init__(self, boolean):
        self.boolean = boolean

    def print(self):
        print(self.boolean, end="")

    def render_graph(self):
        return "True" if self.boolean else "False"

    def compareTo(self, value):
        if not isinstance(value, BooleanValue): return False
        return self.boolean == value.boolean

class FunctionValue(ReferenceValue):
    def __init__(self, gcReference):
        self.gcReference = gcReference

class LambdaValue(ReferenceValue):
    def __init__(self, gcReference):
        self.gcReference = gcReference

class ClassConstructorValue(ReferenceValue):
    def __init__(self, gcReference):
        self.gcReference = gcReference

class ClassValue(ReferenceValue):
    def __init__(self, gc, gcReference):
        super().__init__(gc)
        self.gcReference = gcReference

    def print(self):
        print(self.gc.getObject(self.gcReference), end="")

    def compareTo(self, value):
        if not isinstance(value, ClassValue): return False
        return self.gcReference == value.gcReference

class MethodValue(ReferenceValue):
    def __init__(self, classValue, gcReference):
        self.classValue = classValue
        self.gcReference = gcReference

class ScopeValue(ReferenceValue):
    def __init__(self, gc, gcReference):
        super().__init__(gc)
        self.scope = gc.getObject(gcReference)
        self.gcReference = gcReference

    def setVariable(self, identifier, value):
        self.scope.setVariable(identifier, value)

    def getVariable(self, identifier):
        return self.scope.getVariable(identifier)

    def setRegister(self, value):
        self.scope.setRegister(value)

    def copy(self):
        return self.scope.copy()

    def clearRegisters(self):
        self.scope.clearRegisters()

class NoneValue(Value):
    def __init__(self):
        pass

    def print(self):
        print('None', end="")

    def render_graph(self):
        return "None"

    def compareTo(self, value):
        return isinstance(value, NoneValue)

class BuiltinValue(Value):
    def __init__(self, function):
        self.function = function
