class Value:
    pass

class StringValue(Value):
    def __init__(self, string):
        self.string = string

    def print(self):
        print(self.string)

class NumberValue(Value):
    def __init__(self, number):
        self.number = number

    def print(self):
        print(self.number)

class BooleanValue(Value):
    def __init__(self, boolean):
        self.boolean = boolean

    def print(self):
        print(self.boolean)

class FunctionValue(Value):
    def __init__(self, gcReference):
        self.gcReference = gcReference
