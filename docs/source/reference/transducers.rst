``transducer.transducers``
==========================

.. automodule:: transducer.transducers

  Blah blah blah

.. currentmodule transducer.transducers

Transducer Factories
--------------------

Call these functions to obtain transducer objects.


.. autosummary::
     :nosignatures:

     mapping


.. autofunction:: mapping(transform)

    .. rubric:: Examples

    Mapping a squaring function over a list::

      >>> from transducer.eager import transduce
      >>> from transducer.reducers import appending
      >>> from transducer.transducers import mapping
      >>> m = mapping(lambda x: x*x)
      >>> a = [1, 7, 9, 4, 3, 2]
      >>> transduce(m, appending(), a)
      [1, 49, 9, 4, 3, 2]


.. autofunction:: filtering(predicate)

    .. rubric:: Examples

    Filtering even numbers from a list::

      >>> from transducer.eager import transduce
      >>> from transducer.reducers import appending
      >>> from transducer.transducers import filtering
      >>> f = filtering(lambda x: x % 2 == 0)
      >>> a = [1, 7, 9, 4, 3, 2]
      >>> transduce(f, appending(), a)
      [4, 2]


.. autofunction:: reducing(reducer, init=UNSET)

    .. rubric:: Examples

    Reducing a list of numbers to a single value by summing them::

      >>> from transducer.eager import transduce
      >>> from transducer.reducers import expecting_single
      >>> from transducer.transducers import reducing
      >>> r = reducing(lambda x, y: x + y)
      >>> a = [1, 7, 9, 4, 3, 2]
      >>> transduce(r, expecting_single(), a)
      >>> 26