class Scope:
    def __init__(self, gc, parent):
        self.parent = parent
        self.variables = {}
        self.gc = gc

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
        scope = Scope(self.gc, self.parent)
        scope.variables = self.variables.copy()
        return scope

    def delete(self):
        for k, v in self.variables:
            if isinstance(v, ReferenceValue):
                self.gc.getObject(v.gcReference).delete()
