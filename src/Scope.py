class Scope:
    def __init__(self, parent):
        self.parent = parent
        self.variables = {}

    def setVariable(self, identifier, value):
        tmp = self
        while tmp != None:
            if identifier in tmp.variables:
                tmp.variables[identifier] = value
                return
            tmp = tmp.parent
        self.variables[identifier] = value

    def getVariable(self, identifier):
        if identifier in self.variables:
            return self.variables[identifier]
        if self.parent:
            return self.parent.getVariable(identifier)
        return None

    def copy(self):
        scope = Scope(self.parent)
        scope.variables = self.variables.copy()
        return scope
