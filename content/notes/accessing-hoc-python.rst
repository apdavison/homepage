Accessing hoc from Python
=========================

:date: 2009-01-22
:tags: Python, NEURON
:category: Notes
:slug: accessing-hoc-python
:author: Andrew Davison

When running NEURON with Python, the hoc interpreter is still available from within Python,
and much of the functionality of NEURON is accessed through the hoc interpreter.

The hoc interpreter is accessible either through the ``execute()`` function in
the ``neuron.hoc`` module, or through the automatically-created ``h`` object in
the ``neuron`` module:

.. code-block:: python

    >>> from neuron import h
    >>> h
    TopLevelHocInterpreter

The ``h`` object can be used to access any variable, object reference or
function defined in the hoc interpreter, e.g.:

.. code-block:: python

    >>> h.dt
    0.025000000000000001
    >>> h.t
    0.0
    >>> h.finitialize()
    1.0

and is also callable, with any valid hoc command as the argument, e.g.:

.. code-block:: python

    >>> h('x = 2')
    first instance of x
    1
    >>> h.x
    2.0
    >>> h('create soma')
    1
    >>> h('access soma')
    1
    >>> h.soma
    <nrn.Section object at 0xb7433060>
    >>> h.soma(0.5).v
    -65.0
    >>> h('strdef s')
    1
    >>> h.s = 'hello'
    >>> h.s
    'hello'

Note that the return value of the ``h()`` call (often ``1``) is printed to the
screen. If you don't like this behaviour, you can always assign the return
value to a variable, e.g.:

.. code-block:: python

    >>> tmp = h('x=5')
    >>>

Note that you cannot assign to a variable that has not already been defined:

.. code-block:: python

    >>> h.y = 3
    Traceback (most recent call last):
     File "stdin", line 1, in <module>
    LookupError: 'y' is not a hoc variable name.
    
Objects defined in hoc behave in almost all ways like Python objects, e.g.:

.. code-block:: python

    >>> h('objref vec')
    1
    >>> h('vec = new Vector(5)')
    1
    >>> h('objref list')
    1
    >>> h('list = new List()')
    1
    >>> h.list.append(h.vec)
    1.0
    >>> my_list = h.list
    >>> my_list.count()
    1.0
    >>> my_list.append(h.vec)
    2.0
    >>> my_vec = h.vec
    >>> my_list.append(my_vec)
    3.0
    >>> my_list.object(2)
    Vector[0]
    
Note that in the example above, there is only a single Vector object - assigning
it to a different name or adding it to a list does not copy the Vector:

.. code-block:: python

    >>> h.vec.x[0] = 5
    >>> my_vec.x[1] = 4
    >>> my_list.object(0).x[2] = 3
    >>> my_list.object(1).x[3] = 2
    >>> h.list.object(2).x[4] = 1
    >>> my_vec.printf()
    5       4       3       2       1
    
    5.0
    >>>
    
But in some ways, ``HocObject``\s do not behave as you might expect. For example,
although we showed above that ``my_vec`` and ``h.vec`` reference the same
object:

.. code-block:: python

    >>> my_vec == h.vec
    False
    
Also, all ``HocObject``\s have the same type, whatever the object type in hoc:

.. code-block:: python

    >>> type(my_vec)
    <type 'hoc.HocObject'>
    >>> type(my_list)
    <type 'hoc.HocObject'>


However, listing the object attributes and methods using ``dir(obj)`` lists those of the specific hoc object type,
and ``help(obj)`` gives help about the object's hoc type.

