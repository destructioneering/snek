class Object:
    def __init__(self):
        pass

class Function(Object):
    def __init__(self, scope, parameters, body, evaluator):
        self.scope = scope
        self.parameters = parameters
        self.body = body
        self.evaluator = evaluator

    def apply(self, arguments):
        if len(self.parameters) != len(arguments):
            print('Incorrect number of arguments supplied to function')
        for i in range(len(arguments)):
            self.scope[parameters[i]] = arguments[i]
        return self.evaluator.eval(self.body)
