class GarbageCollector:
    def __init__(self):
        self.objects = []
        self.objectIndex = 0

    def allocate(self, obj):
        self.objects.append(obj)
        self.objectIndex += 1
        return self.objectIndex - 1

    def getObject(self, index):
        return self.objects[index]
