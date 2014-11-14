Installation of NEURON with Python
==================================

:date: 2008-03-19 10:20
:tags: Python, NEURON
:category: Notes
:slug: installation-neuron-python
:author: Andrew Davison

*Updated 2009-01-22 for NEURON v7.0*

These instructions are for NEURON_ v7.0. They may remain valid for future
versions, and should also work for v6.1 or newer. These instructions are for Linux  or Mac OS X, using the bash shell. They may well work in Cygwin, but
I haven't tested them.

Binary versions of NEURON 7.0 come with Python_ support, and allow you to
run ``nrniv -python`` (embedded Python), but they don't allow you to run Python (or IPython_) and then do ``import neuron`` (NEURON as a Python module): for this you need to compile from source_.

.. _NEURON: http://www.neuron.yale.edu/neuron/
.. _Python: http://www.python.org/
.. _IPython: http://ipython.scipy.org/
.. _source: http://www.neuron.yale.edu/neuron/download/getstd


First build and install Interviews, if you don't already have it::

    $ N=`pwd`
    $ tar xzf iv-17.tar.gz
    $ cd iv-17
    $ ./configure --prefix=`pwd`
    $ make
    $ make install
    
Now build and install NEURON::

    $ cd ..
    $ tar xzf nrn-7.0.tar.gz
    $ cd nrn-7.0
    $ ./configure --prefix=`pwd` --with-iv=$N/iv-17 --with-nrnpython
    $ make
    $ make install
    
If you want to run parallel NEURON, add ``--with-paranrn`` to the ``configure``
options. On Mac OS X, I have found I need to add ``PYLIB=-lpython PYLIBLINK=-lpython`` to the ``configure`` line.

Now add the NEURON ``bin`` directory to your ``PATH``::

    $ export PATH=$N/nrn-7.0/i686/bin:$PATH

(Replace ``i686`` with your own CPU architecture if necessary).

Now build the NEURON shared library for Python::

    $ cd src/nrnpython
    # python setup.py install
    
This command (which will probably have to be run as root or using ``sudo``) will
install the ``neuron`` package to your ``site-packages`` directory. An
alternative, especially if you don't have root privileges, is::

    $ python setup.py install --prefix=~
    
which will install the ``neuron`` package to ``~/lib/python/site-packages``.
You will then have to add this directory to the ``PYTHONPATH`` environment
variable::

    $ export PYTHONPATH=$PYTHONPATH:~/lib/python/site-packages
    
Starting NEURON
---------------

For those who are not familiar with NEURON, it may be started without the
graphical interface using ``nrniv`` or with the graphical interface using
``nrngui``. To use Python, rather than hoc, as the interpreter, use the
``-python`` option::

    $ nrniv -python
    NEURON -- Release 7.0 (281:80827e3cd201) 2009-01-16
    Duke, Yale, and the BlueBrain Project -- Copyright 1984-2008
    See http://www.neuron.yale.edu/credits.html

    >>> import neuron
    >>>
    
If there are any NEURON extension (NMODL) mechanisms in the working directory,
and they have been compiled with ``nrnivmodl``, they will be loaded
automatically.


Alternatively, you may wish to use the normal Python interpreter, or an
alternative such as IPython. In this case, NEURON is started (and any
NMODL mechanisms loaded) when you ``import neuron``::

    $ ipython
    Python 2.4.1 (#1, May 25 2007, 17:56:29)
    Type "copyright", "credits" or "license" for more information.
    
    IPython 0.6.15 -- An enhanced Interactive Python.
    ?       -> Introduction to IPython's features.
    %magic  -> Information about IPython's 'magic' % functions.
    help    -> Python's own help system.
    object? -> Details about 'object'. ?object also works, ?? prints more.
    
    In [1]: import neuron
    NEURON -- Release 7.0 (281:80827e3cd201) 2009-01-16
    Duke, Yale, and the BlueBrain Project -- Copyright 1984-2008
    See http://www.neuron.yale.edu/credits.html

    In [2]:
