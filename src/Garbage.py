class GarbageCollector:
    def __init__(self):
        self.objects = []
        self.objectIndex = 0

    def allocate(self, obj):
        self.objects.append(obj)
        self.objectIndex += 1
        return self.objectIndex - 1

    def delete(self, idx):
        pass

    def getObject(self, idx):
        return self.objects[idx]

class ReferenceCounter(GarbageCollector):
    def delete(self, idx):
        self.objects[idx].referenceCount -= 1

        if self.objects[idx].referenceCount == 0:
            self.objects[idx].delete()
            # idx is now free to reassign.
