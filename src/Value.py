class Value:
    pass

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

class NoneValue(Value):
    def print(self):
        print('None')

    def compareTo(self, value):
        return isinstance(value, NoneValue)
