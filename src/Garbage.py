import logging

from Value import *
from Object import *

class ReferenceCounter:
    # This should never be called on an object after the
    # referenceCount has hit zero. That would mean that the object is
    # still being referenced by some system that thinks it's alive
    # after the object was marked dead. Very bad.
    def subReference(self, gc, idx):
        gc.objects[idx].referenceCount -= 1
        logging.debug('-- %s', gc.p(idx))

        if gc.objects[idx].referenceCount < 0:
            # logging.debug('====================================', gc.objects[idx], gc.objects[idx].referenceCount)
            abort()

        if gc.objects[idx].referenceCount == 0:
            logging.debug('object dying: %s', gc.p(idx))
            gc.objects[idx].delete()
            #gc.objects[idx] = None
            # idx is now free to reassign.
            pass

class GarbageCollector:
    def __init__(self):
        self.objects = []
        self.objectIndex = 0
        self.referenceCounter = ReferenceCounter()

    def p(self, idx):
        obj = self.objects[idx]
        return f"<object idx='{idx}' type='{type(obj)}' references='{obj.referenceCount}'>"

    def allocate(self, obj):
        self.objects.append(obj)
        logging.debug('allocating %s', self.p(self.objectIndex))
        obj.idx = self.objectIndex
        self.objectIndex += 1
        return self.objectIndex - 1

    def getObject(self, idx):
        return self.objects[idx]

    def subReference(self, value, varname="no variable"):
        if isinstance(value, ReferenceValue):
            self.referenceCounter.subReference(self, value.gcReference)
        if isinstance(value, Object):
            self.referenceCounter.subReference(self, value.idx)

    def addReference(self, value):
        if isinstance(value, ReferenceValue):
            self.objects[value.gcReference].referenceCount += 1
            logging.debug('++ %s', self.p(value.gcReference))
        if isinstance(value, Object):
            self.objects[value.idx].referenceCount += 1
            logging.debug('++ %s', self.p(value.gcReference))
