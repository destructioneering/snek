from Value import *

class Scope:
    def __init__(self, gc, parent):
        self.parent = parent
        self.variables = {}
        self.gc = gc
        self.objects = []

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
        # for idx in self.objects:
        #     self.gc.addReference(idx)
        return scope

    def delete(self):
        for idx in self.objects:
            self.gc.delete(idx)

    def addObject(self, idx):
        self.objects.append(idx)
        self.gc.addReference(idx)
