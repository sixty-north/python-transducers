=====================
Transducers in Python
=====================

Transducers are functions which transform reducers - hence the name.
A reducer, in this case, is any function which you could pass to the
``reduce()`` function in the Python Standard Library ``functools``
module. Such reducers accept an initial or intermediate result and
combine a new value with that result to produce a new (or updated)
result.  Transducers provide us with a convenient means to compose
simple reducers into more complex and capable reducers.

Furthermore, transducers facilitate the clean separation of
concerns concerns of how source values are input, how they are
processed by reducers, and the how results output. This allows the
same transducers to be (re)used with many sources and destinations
of data, not just with iterable series.

Transducers were developed by Rich Hickey, the driving force behind
the Clojure programming language, and this package aims to bring
the benefits of transducers to Python, whilst transforming some of
the Clojurisms into more Pythonic solutions.

This package, which is most definitely a work in progress and a
vehicle for ongoing research into transducers in Python, implements
simple infrastructure for implementing transducers in Python, a
selection of transducer implementations of common operations, and
some 'transducible processes' which allow us to apply transducers
to iterable series (both eagerly and lazily) and to use
transducers to process 'push' events implemented as Python
coroutines.
