``transducer.eager``
====================

.. automodule:: transducer.eager

  Blah blah blah

  .. autosummary::
     :nosignatures:

     .. currentmodule transducer.eager

     transduce

  .. autofunction:: transduce(transducer, reducer, iterating, init=UNSET)

     .. rubric:: Examples

     Eager transduction of a mapping over a list::

       >>> from transducer.eager import transducer
       >>> from transducer.reducers import appending
       >>> from transducer.transducers import mapping
       >>> m = mapping(lambda x: x*x)
       >>> a = [1, 7, 9, 4, 3, 2]
       >>> transduce(mapping, appending(), a)
       [1, 49, 9, 4, 3, 2]


