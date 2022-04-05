from Value import *

class Object:
    def __init__(self, id):
        self.id = id

class FunctionObject(Object):
    def __init__(self, scope, parameters, body, evaluator):
        self.scope = scope
        self.parameters = parameters
        self.body = body
        self.evaluator = evaluator

    def apply(self, arguments):
        if len(self.parameters) != len(arguments):
            print('Incorrect number of arguments supplied to function')
        for i in range(len(arguments)):
            self.scope[self.parameters[i]] = arguments[i]
        self.evaluator.evalStatement(self.scope, self.body)

        # This should return something real in the future.
        return StringValue('it worked')
