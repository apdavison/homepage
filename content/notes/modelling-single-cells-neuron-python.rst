Modelling single cells in NEURON with the Python interpreter
============================================================

:date: 2008-03-23 10:20
:tags: Python, NEURON
:category: Notes
:slug: modelling-single-cells-neuron-python
:author: Andrew Davison

*(updated for NEURON 7.0 on 2009-01-25)*

This is an introduction to using the Python interpreter to build simple single
cell models with the NEURON simulator. I assume some familiarity with Python and
with the standard NEURON interpreter, hoc.

Also see notes on `building/installing NEURON with Python`_ and on `accessing hoc from Python`_. 
For more information, see the `NEURON documentation`_.

To get started, either run NEURON with the ``-python`` option::

    $ nrniv -python
    
or use another python interpreter, such as ``python`` or ``ipython``::

    $ python
    
Then import the ``neuron`` and ``nrn`` modules:

.. code-block:: python

    >>> from neuron import *
    >>> from nrn import *

The order is important if using an ordinary Python interpreter: ``nrn`` is not
available until after ``neuron`` has been imported.



Creating a membrane section and manipulating its attributes
-----------------------------------------------------------

Membrane sections are represented by ``Section`` objects. They are
instantiated with no arguments (although in the future it would be nice to be
able to set section properties in the constructor):

.. code-block:: python

    >>> soma = Section()
    >>> type(soma)
    <type 'nrn.Section'>

As in hoc, a section's length, axial resistance and number of segments may be
accessed and changed using dot notation:

.. code-block:: python

    >>> soma.L
    100.0
    >>> soma.nseg
    1
    >>> soma.Ra
    35.399999999999999
    >>> soma.nseg = 3
    >>> soma.nseg
    3
    
Each segment of the section may be accessed in turn by iterating over the
section:

.. code-block:: python

    >>> for seg in soma:
    ...   print seg.x, seg.diam
    ...
    0.166666666667 500.0
    0.5 500.0
    0.833333333333 500.0
    
or an individual segment may be accessed by calling the ``Section`` object with
the x-location (0-1) as an argument:

.. code-block:: python

    >>> central_seg = soma(0.5)
    >>> type(central_seg)
    <type 'nrn.Segment'>
    >>> central_seg.diam
    500.0
    
Note the difference in syntax with respect to hoc:

.. code-block:: python

    oc> soma.v(0.5)
        -65
    >>> soma(0.5).v
    -65.0
    
    
The currently-accessed section
------------------------------

The concept of the currently-accessed section is less important in Python than
in hoc, but it exists nonetheless. When we created the ``soma`` section above,
it became the currently accessed section by default. The function ``cas()`` in
the ``nrn`` module returns the currently accessed section as a ``Section``
object:

.. code-block:: python

    >>> soma.name()
    'PySec_402d1040'
    >>> cas().name()
    'PySec_402d1040'
    
If we now create a new section, ``soma`` is still the currently-accessed
section:

.. code-block:: python

    >>> dend = Section()
    >>> soma == cas()
    True
    >>> dend == cas()
    False
    
To make ``dend`` the currently-accessed section, use its ``push()`` method:

.. code-block:: python

    >>> dend.push()
    >>> dend == cas()
    True
    
We can now perform operations on dend using hoc calls, e.g.:

.. code-block:: python

    >>> dend.L
    100.0
    >>> h('L = 200')
    1
    >>> dend.L
    200.0
    
(The '``h``' ``HocObject`` comes from the ``neuron`` module. For more information
on ``HocObject``\s, see `accessing hoc from Python`_).

To return to the previously-access section, use the hoc ``pop_section()``
function:

.. code-block:: python

    >>> h.pop_section()
    1.0
    >>> soma == cas()
    True
    
    
Connecting sections together
----------------------------

To connect two sections, call the ``connect()`` method of the child ``Section``
object with the parent section as the argument:

.. code-block:: python

    >>> dend.connect(soma)
    
By default, the '``0``' end of the child is connected to the '``1``' end of the
parent. Which point on the parent to connect to and which end of the child to
connect can be controlled with additional, optional arguments:

.. code-block:: python

    >>> axon = Section()
    >>> axon.connect(soma, 0.1, 1)
    >>> for sec in dend, axon:
    ...   sec.push()
    ...   h.psection()
    ...   h.pop_section()
    ...
    <nrn.Section object at 0x402d1050>
    PySec_402d1050 { nseg=1  L=200  Ra=35.4
            PySec_402d1040 connect PySec_402d1050 (0), 1
            /* First segment only */
            insert morphology { diam=500}
            insert capacitance { cm=1}
    }
    <nrn.Section object at 0x402d1060>
    PySec_402d1060 { nseg=1  L=100  Ra=35.4
            PySec_402d1040 connect PySec_402d1060 (1), 0.1
            /* First segment only */
            insert morphology { diam=500}
            insert capacitance { cm=1}
    }
    
It is often not necessary to explicitly push the section onto the stack, as most functions take an optional ``sec`` keyword argument:

.. code-block:: python

    >>> h.psection(sec=soma)
    PySec_402d1040 { nseg=3  L=100  Ra=35.4
        /*location 0 attached to cell 0*/
        /* First segment only */
        insert capacitance { cm=1}
        insert morphology { diam=500}
    }   


Inserting membrane mechanisms
-----------------------------

.. code-block:: python

    >>> soma.insert('pas')

Accessing range variables can be done in two ways: using a more object-oriented notation:

.. code-block:: python

    >>> soma(0.5).pas.g
    0.001
    >>> soma(0.5).pas.e
    -70.0
    
or with a more hoc-compatible syntax using underscores:

.. code-block:: python

    >>> soma(0.5).g_pas
    0.001
    >>> soma(0.5).e_pas
    -70.0

Contrast with the hoc syntax:

.. code-block:: python

    oc> soma.g_pas(0.5)
             0.001
    oc> soma.e_pas(0.5)
             -70
             
To set values for all the segments in a section, iterate over them:

.. code-block:: python

    >>> for seg in soma:
    ...     seg.pas.g = 0.01*seg.x
    
Or, to set the same value for all segments:

.. code-block:: python

    >>> soma(0.5).e_pas = -64.0

For the most fine-scale control, the mechanisms can be addressed as Python objects:

.. code-block:: python

    for seg in soma:
    ...   for mech in seg:
    ...     if mech.name() == 'pas':
    ...       print seg.x, mech.g, mech.e
    ...
    0.166666666667 0.00166666666667 -64.0
    0.5 0.005 -64.0
    0.833333333333 0.00833333333333 -64.0


Creating and inserting point processes
--------------------------------------

All hoc classes are accessible in Python through the ``h`` object. Of these,
point processes such as ``IClamp``\s must be associated with a membrane section,
so we must either push the section onto the stack using, e.g. ``soma.push()``, or, 
which is more convenient, pass the section as the ``sec`` keyword argument:

.. code-block:: python
    
    >>> stim = h.IClamp(0.5, sec=soma)
    >>> type(stim)
    <type 'hoc.HocObject'>
    >>> stim.amp
    0.0
    >>> stim.dur
    0.0
    >>> stim.del
      File "<stdin>", line 1
        stim.del
               ^
    SyntaxError: invalid syntax

What happened there? ``del`` is a reserved word in Python, which sometimes
conflicts with names in hoc. For this reason, the ``IClamp`` delay attribute, which is
called ``del`` in hoc, has been renamed to ``delay`` in Python::

    >>> stim.delay = 50.0

Note, however, that the original name can still be accessed using the Python 
``getattr()`` and ``setattr()`` functions:

.. code-block:: python

    >>> getattr(stim, 'del')
    50.0
    >>> setattr(stim, 'del', 100.0)
    >>> stim.delay
    100.0
   

.. _`NEURON documentation`: http://www.neuron.yale.edu/neuron/static/docs/help/neuron/neuron/classes/python.html
.. _`building/installing NEURON with Python`: /notes/installation-neuron-python/
.. _`accessing hoc from Python`: /notes/installation-neuron-python/
