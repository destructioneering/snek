class Value:
    def __init__(self, gc):
        self.gc = gc

class StringValue(Value):
    def __init__(self, string):
        self.string = string

    def print(self):
        print(self.string)

    def compareTo(self, value):
        if not isinstance(value, StringValue): return False
        return self.string == value.string

class NumberValue(Value):
    def __init__(self, number):
        self.number = number

    def print(self):
        print(self.number)

    def compareTo(self, value):
        if not isinstance(value, NumberValue): return False
        return self.number == value.number

class BooleanValue(Value):
    def __init__(self, boolean):
        self.boolean = boolean

    def print(self):
        print(self.boolean)

    def compareTo(self, value):
        if not isinstance(value, BooleanValue): return False
        return self.boolean == value.boolean

class FunctionValue(Value):
    def __init__(self, gcReference):
        self.gcReference = gcReference

class LambdaValue(Value):
    def __init__(self, gcReference):
        self.gcReference = gcReference

class ClassConstructorValue(Value):
    def __init__(self, gcReference):
        self.gcReference = gcReference

class ClassValue(Value):
    def __init__(self, gc, gcReference):
        super().__init__(gc)
        self.gcReference = gcReference

    def print(self):
        print(self.gc.getObject(self.gcReference))

    def compareTo(self, value):
        if not isinstance(value, ClassValue): return False
        return self.gcReference == value.gcReference

class MethodValue(Value):
    def __init__(self, classValue, functionValue):
        self.classValue = classValue
        self.functionValue = functionValue

class NoneValue(Value):
    def __init__(self):
        pass

    def print(self):
        print('None')

    def compareTo(self, value):
        return isinstance(value, NoneValue)

class BuiltinValue(Value):
    def __init__(self, function):
        self.function = function
