From Hoc to Python: a case study
================================

:date: 2010-11-10
:tags: Python, NEURON
:category: Notes
:slug: hoc-to-python-bulbnet
:author: Andrew Davison


Although I was involved in the process of adding Python_ support to the NEURON_
simulator, and in writing a `paper about this`_, I've never converted a complete,
published model from Hoc to Python.

There is in fact no strong reason for doing so, since an existing Hoc file can be
executed from Python using:

.. code-block:: python

    >>> from neuron import h
    >>> h.xopen(filename)

after which any variables or object references declared in *filename* will be
available through the ``h`` object.

Nevertheless, if you want to modify and build upon an existing model, converting
it to Python may give you a more flexible and powerful base upon which to build.

The model I chose to convert is one I developed during my PhD thesis, of the
mammalian olfactory bulb (`Davison, Feng and Brown (2003) J. Neurophysiol. 90:1921-1935`_).
The original code for the model is available on `ModelDB with accession number 2730`_,
but since I would be extending it, I copied it to a Mercurial_ repository on
BitBucket_. To checkout a copy::

    $ hg clone http://bitbucket.org/apdavison/bulbnet
    
Ion channels
------------

Several of the ion channel models use tabulated data, rather than equations,
to define their rate functions. This means that in the NMODL_ definition there
are a number of ``FUNCTION_TABLE`` statements, e.g., in kfasttab.mod_::

    FUNCTION_TABLE tabntau(v(mV)) (ms)

When this mechanism is loaded into NEURON, a ``table_tabntau_kfasttab()`` procedure
appears in Hoc. This procedure must be called in order to populate the table. In
Hoc::

    oc> table_tabntau_kfasttab(&datavec.x[0], vvec.size, &vvec.x[0])

where ``datavec`` is a ``Vector`` containing the values of ``tau`` and ``vvec``
contains the values of the membrane potential. In Python, this becomes:

.. code-block:: python

    >>> h.table_tabntau_kfasttab(datavec._ref_x[0], vvec.size(), vvec._ref_x[0])

The original Hoc file that populated the rate tables is tabchannels.hoc_, the
Python version is in tabchannels.py_. Again, there was no real reason to do this,
as the same thing could be achieved using:

.. code-block:: python

    >>> h.xopen("tabchannels.hoc")

Cell models
-----------

The mitral and granule cell models are defined in Hoc templates. These become
classes in Python, e.g.:

.. code-block:: python

    >>> h.xopen("mitral.tem")
    >>> h.xopen("granule.tem")
    >>> mitral_cell = h.Mit()
    >>> granule_cell = h.Gran()

and can even be subclassed, to add new functionality::

    >>> class Mit2(hclass(h.Mit)):
    ...    pass
    >>> another_mitral_cell = Mit2()
    
However, again I decided to redefine the ``Mit`` and ``Gran`` models from scratch
as pure Python classes.

One of the potential benefits of using Python with NEURON is less verbose code -
hiding book-keeping details within classes makes the structure of the model
shorter and easier to understand. For example, to insert an ion channel into a
section and set its parameters we can do::

    >>> soma = h.Section()
    >>> soma.insert('hh')
    >>> for segment in soma:
    ...     segment.hh.gnabar = 0.11
    ...     segment.hh.gkbar = 0.03
    ...     segment.hh.gl = 0.0004
    ...     segment.hh.el = -55

This is not so bad, but if there are many ion channels with many parameters, we
end up with a lot of lines of code. If we define, in a separate file, a
``Mechanism`` class as follows:

.. code-block:: python

    class Mechanism(object):
        def __init__(self, name, **parameters):
            self.name = name
            self.parameters = parameters

        def insert_into(self, section):
            section.insert(mechanism.name)
            for name, value in self.parameters.items():
                for segment in section:
                    mech = getattr(segment, mechanism.name)
                    setattr(mech, name, value)

then the code to insert an ion channel into the soma reduces from six lines to
two:

.. code-block:: python

    >>> hh = Mechanism('hh', gnabar=0.11, gkbar=0.03, gl=0.0004, el=-55)
    >>> hh.insert_into(soma)

Similarly, I defined a new ``Section`` class, which subclasses ``h.Section`` but
allows the length, diameter, axial resistivity, ion channel mechanisms and
connections to other sections all to be specified in the constructor, i.e.,
we can reduce:

.. code-block:: python

    >>> dend = h.Section()
    >>> dend.L = 50
    >>> dend.diam = 2.0
    >>> dend.Ra = 100.0
    >>> dend.insert('hh')
    >>> for segment in dend:
    ...     segment.hh.gnabar = 0.11
    ...     segment.hh.gkbar = 0.03
    ...     segment.hh.gl = 0.0004
    ...     segment.hh.el = -55
    >>> dend.connect(soma, 1, 0)

to a single line:

.. code-block:: python

    >>> dend.Section(L=50, diam=2.0, Ra=100.0, mechanisms=[hh], parent=soma, connect_to=1)

Similarly, inserting a synapse goes from:

.. code-block:: python

    >>> dend_AMPAr = ExpSyn(0.5, sec=dend)
    >>> dend_AMPAr.e = 0.0
    >>> dend_AMPAr.tau = 2.0

to:

.. code-block:: python

    >>> dend.add_synapse("AMPAr", "ExpSyn", e=0.0, tau=2.0)
    
with the added advantage that the synapse object is now available as ``dend.AMPAr``,
i.e. it is contained within the dend object, so we don't have to keep track of
clumsy names like ``dend_AMPAr``.


The ``Mechanism`` and ``Section`` classes have the potential to be useful in
many projects, so I have put them into a separate package, *nrnutils*, available
from http://pypi.python.org/pypi/nrnutils/. To use it in your own code, install
using::

    $ easy_install nrnutils
    
(this requires setuptools_. If you don't have this, full installation instructions
are on the nrnutils PyPI page) then in Python:

.. code-block:: python

    >>> from nrnutils import Mechanism, Section

If you have your own useful Python classes or functions for NEURON, I would be
happy to add them into *nrnutils*, or why not release your own Python package.
The development repository for *nrnutils* is at http://bitbucket.org/apdavison/nrnutils.

The original cell templates are at mitral.tem_ and granule.tem_, the Python
versions are at mitral.py_ and granule.py_.




.. _Python: http://www.python.org/
.. _NEURON: http://www.neuron.yale.edu/neuron/
.. _`paper about this`: http://www.frontiersin.org/neuroinformatics/10.3389/neuro.11/001.2009/abstract
.. _`Davison, Feng and Brown (2003) J. Neurophysiol. 90:1921-1935`: http://intl-jn.physiology.org/cgi/content/abstract/90/3/1921
.. _`ModelDB with accession number 2730`: http://senselab.med.yale.edu/modeldb/ShowModel.asp?model=2730
.. _Mercurial: http://mercurial.selenic.com/
.. _BitBucket: http://bitbucket.org/
.. _NMODL: http://www.neuron.yale.edu/neuron/static/papers/nc2000/nmodl.htm
.. _kfasttab.mod: http://bitbucket.org/apdavison/bulbnet/src/0191a439827a/kfasttab.mod
.. _tabchannels.hoc: http://bitbucket.org/apdavison/bulbnet/src/0191a439827a/tabchannels.hoc
.. _tabchannels.py: http://bitbucket.org/apdavison/bulbnet/src/0191a439827a/python/tabchannels.py
.. _setuptools: http://pypi.python.org/pypi/setuptools
.. _mitral.tem: http://bitbucket.org/apdavison/bulbnet/src/0191a439827a/mitral.tem
.. _granule.tem: http://bitbucket.org/apdavison/bulbnet/src/0191a439827a/granule.tem
.. _mitral.py: http://bitbucket.org/apdavison/bulbnet/src/0191a439827a/python/mitral.py
.. _granule.py: http://bitbucket.org/apdavison/bulbnet/src/0191a439827a/python/granule.py
