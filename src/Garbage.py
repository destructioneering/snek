class ReferenceCounter:
    # This should never be called on an object after the
    # referenceCount has hit zero.
    def delete(self, gc, idx):
        gc.objects[idx].referenceCount -= 1

        if gc.objects[idx].referenceCount < 0:
            print('====================================', gc.objects[idx], gc.objects[idx].referenceCount)

        if gc.objects[idx].referenceCount == 0:
            # gc.objects[idx].delete()
            #gc.objects[idx] = None
            # idx is now free to reassign.
            pass

        print(gc.objects)

class GarbageCollector:
    def __init__(self):
        self.objects = []
        self.objectIndex = 0
        self.referenceCounter = ReferenceCounter()

    def allocate(self, obj):
        self.objects.append(obj)
        self.objectIndex += 1
        return self.objectIndex - 1

    def delete(self, idx, varname="no variable"):
        # print(f"Deleting variable {varname}")
        self.referenceCounter.delete(self, idx)

    def addReference(self, idx):
        self.objects[idx].referenceCount += 1
        print(f"GC Adding reference to {idx} (now {self.objects[idx].referenceCount})")

    def getObject(self, idx):
        return self.objects[idx]
