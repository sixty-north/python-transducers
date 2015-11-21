=====================
Transducers in Python
=====================

This is a port of the *transducer* concept from Clojure to Python,
with an emphasis on providing as Pythonic as interpretation of
transducers as possible, rather than reproducing Clojurisms more
literally.

Installable Python package
==========================

This package is available on the Python Package Index (PyPI) as
`transducer <https://pypi.python.org/pypi/transducer/>`_.

Status
======

Build status:

.. image:: https://travis-ci.org/sixty-north/python-transducers.svg?branch=master
    :target: https://travis-ci.org/sixty-north/python-transducers
    :alt: Build Status

.. image:: https://readthedocs.org/projects/python-transducers/badge/?version=latest
    :target: https://readthedocs.org/projects/python-transducers/?badge=latest
    :alt: Documentation Status

Note: Documentation is very much a work in progress.

What are transducers?
=====================

Transducers are functions which transform reducers - hence the name.
A reducer, in this case, is any function which you could pass to the
``reduce()`` function in the Python Standard Library ``functools``
module. Such reducers accept an initial or intermediate result and
combine a new value with that result to produce a new (or updated)
result.  Transducers provide us with a convenient means to compose
simple reducers into more complex and capable reducers.

Furthermore, transducers facilitate the clean separation of
concerns of how source values are input, how they are
processed by reducers, and the how results output. This allows the
same transducers to be (re)used with many sources and destinations
of data, not just with iterable series.

Transducers were developed by Rich Hickey, the driving force behind
the Clojure programming language, and this package aims to bring
the benefits of transducers to Python 3, whilst transforming some of
the Clojurisms into more Pythonic solutions.

An extended write-up of the development of Python transducers from
scratch can be found in our series of articles
`Understanding Transducers Through Python <http://sixty-north.com/blog/series/understanding-transducers-through-python>`_.
The code developed over the course of these articles is substantially
the same as in this ``transducer`` package, although the package uses
some further abstractions and tools which are largely irrelevant to
understanding how transducers work.

This package, implements simple infrastructure for implementing
transducers in Python, a selection of transducer implementations of
common operations, and some 'transducible processes' which allow us
to apply transducers to iterable series (both eagerly and lazily) and
to use transducers to process 'push' events implemented as Python
coroutines.
