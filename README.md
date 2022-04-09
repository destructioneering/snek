# Snek

A toy language for experimentation with garbage collection algorithms.

## Garbage collectors

An evaluator contains a single GarbageCollector instance which is used
for all allocations in that evaluation context. The GarbageCollector
contains all three garbage collectors, which share the allocation
space. That is, none of them actually destroy any objects. Their job
is only to report which objects should be considered dead and which
should should be considered dead.

### Reference counter

The first GC system is a reference counter. It involves three systems:

+ Object.py
+ Scope.py
+ Garbage.py

The object has a ~referenceCount~ which is updated by the garbage
collector whenever ~delete()~ is called on an object. ~delete()~ is
not called objects directly by the evaluator, however; the evaluator
calls ~clearRegisters()~ on a scope after each expression evaluation
and ~clearRegisters()~ is responsible for calling ~delete()~ on each
object that was created during an expression evaluation. Note that
variable assignments create additional references, which prevents a
program like:

    x = lambda x: x

... from having the lambda deleted after the expression is
evaluated. When a scope is left the evaluator calls ~delete()~ on it,
which removes those variable references. In the program above, for
example, the lambda will receive its first reference when the scope
adds it to a register and another when it's assigned to the
variable. After the expression is evaluated the registers are cleared,
and the reference count on the lambda is decreased to 1. When the
scope is left there are no references remaining and the lambda object
is collected.

### Tri-color mark-and-sweep

### Tracing
