from Value import *

class ReferenceCounter:
    # This should never be called on an object after the
    # referenceCount has hit zero. That would mean that the object is
    # still being referenced by some system that thinks it's alive
    # after the object was marked dead. Very bad.
    def delete(self, gc, idx):
        gc.objects[idx].referenceCount -= 1

        if gc.objects[idx].referenceCount < 0:
            print('====================================', gc.objects[idx], gc.objects[idx].referenceCount)
            abort()

        if gc.objects[idx].referenceCount == 0:
            gc.objects[idx].delete()
            #gc.objects[idx] = None
            # idx is now free to reassign.
            pass

class GarbageCollector:
    def __init__(self):
        self.objects = []
        self.objectIndex = 0
        self.referenceCounter = ReferenceCounter()

    def allocate(self, obj):
        self.objects.append(obj)
        self.objectIndex += 1
        return self.objectIndex - 1

    def getObject(self, idx):
        return self.objects[idx]

    def subReference(self, value, varname="no variable"):
        if not isinstance(value, ReferenceValue):
            return
        self.referenceCounter.delete(self, value.gcReference)

    def addReference(self, value):
        if not isinstance(value, ReferenceValue):
            return
        self.objects[value.gcReference].referenceCount += 1
