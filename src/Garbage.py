import logging

from Value import *
from Object import *

class GarbageCollector:
    def __init__(self, evaluator):
        self.objects = []
        self.objectIndex = 0

        self.evaluator = evaluator

        self.hide_functions = True
        self.hide_scopes = True
        self.hide_parents = False
        self.hide_dead = False

    def p(self, idx):
        obj = self.objects[idx]
        #return f"<object idx='{idx}' type='{type(obj).__name__}' references='{obj.referenceCount}'>"
        return f"{type(obj).__name__[0:-6]}[{idx}]/{obj.referenceCount}"

    def new_frame(self):
        self.evaluator.events[-1]['frames'].append('');

    def trace(self, scope):
        for obj in self.objects:
            if obj:
                obj.color = 0

        self.objects[0].trace()
        scope.scope.trace()

        header = self.render_graph()[0:-2]
        sofar = ''
        result = []

        for frame in self.evaluator.events[-1]['frames']:
            sofar += frame
            result.append(header + sofar + '}\n')

        result.pop()

        dead = ''

        for obj in self.objects:
            if self.hide_functions and isinstance(obj, FunctionObject): continue
            if self.hide_scopes and isinstance(obj, ScopeObject): continue
            if obj.color != 2 and not (self.hide_dead and obj.referenceCount < 1):
                dead += f'{obj.idx} [fillcolor=red];\n'

        result.append(header + sofar + dead + '}\n')

        self.evaluator.events[-1]['frames'] = result

    def render_graph(self):
        result = 'digraph {\n"" [shape=none];\n"" -> 0;0 [label="Global Scope"];\n'

        for obj in self.objects:
            if not obj: continue
            if self.hide_functions and isinstance(obj, FunctionObject): continue
            if self.hide_functions and isinstance(obj, LambdaObject): continue
            result += obj.render_graph()

        result += '}\n'

        return result

    def allocate(self, obj):
        self.objects.append(obj)
        logging.debug('allocating %s', self.p(self.objectIndex))
        obj.idx = self.objectIndex
        self.objectIndex += 1
        return self.objectIndex - 1

    def getObject(self, idx):
        return self.objects[idx]

    # This should never be called on an object after the
    # referenceCount has hit zero. That would mean that the object is
    # still being referenced by some system that thinks it's alive
    # after the object was marked dead. Very bad.
    def subReference2(self, gc, idx):
        gc.objects[idx].referenceCount -= 1
        logging.debug('-- %s', gc.p(idx))

        if gc.objects[idx].referenceCount < 0:
            # logging.debug('====================================', gc.objects[idx], gc.objects[idx].referenceCount)
            abort()

        if gc.objects[idx].referenceCount == 0:
            logging.debug('object dying: %s', gc.p(idx))
            gc.objects[idx].subReference()
            # gc.objects[idx] = None
            # idx is now free to reassign.

    def subReference(self, value):
        if isinstance(value, ReferenceValue):
            self.subReference2(self, value.gcReference)
        if isinstance(value, Object):
            self.subReference2(self, value.idx)

    def addReference(self, value):
        if isinstance(value, ReferenceValue):
            self.objects[value.gcReference].referenceCount += 1
            logging.debug('++ %s', self.p(value.gcReference))
        if isinstance(value, Object):
            self.objects[value.idx].referenceCount += 1
            logging.debug('++ %s', self.p(value.idx))
