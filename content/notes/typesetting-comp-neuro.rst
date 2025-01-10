Typesetting subscripts, units and physical quantities
=====================================================

:date: 2025-01-10
:tags: LaTeX
:category: Notes
:slug: typesetting-comp-neuro
:author: Andrew Davison

My brain is a nitpicker.
I am easily distracted by small imperfections and inconsistencies,
which is a handicap when reviewing (both for scientific articles and for code)
because minor details such as spelling mistakes or non-standard code style
interfere with my ability to take in the big picture.

An example of such minor details, one that I encounter a lot,
is the typesetting of subscripts, units, and physical quantities
in manuscripts I am asked to review,
which are typically in the fields of computational neuroscience,
neuroinformatics, data science or neuromorphic computing.

When I encounter such problems,
unless I know that the journal in question will fix the typesetting,
I usually flag them in my comments to the authors, as minor issues.
Whenever this occurs, I spend time searching the web for references to the rules that are being broken,
because I never remember them.

This article, then, is mostly written for myself,
to collect these references in one place so that I can easily find them again!

Subscripts and superscripts
---------------------------

The general rule for typesetting mathematics that is most often broken here is:

    Symbols that represent variables should be italicized, all other terms should not be italicized.

For more details on this, see the `Please Make A Note blog`_
or `"Typefaces"`_ from the US National Institute of Standards and Technology (NIST)
(the ultimate reference for this is the `ISO 80000 standard`_, but that is not a very accessible document.)

What this means for subscripts (and superscripts) is that if the subscript represents a variable it should be in italics:

.. math::

    V_x \qquad E^{i}_{y}

but if it is a descriptive term, or a number, it should be in an upright (also called roman) font style:

.. math::

    V_{\mathrm{soma}} \qquad V_{\mathrm{m}} \qquad E_{\mathrm{NMDA}} \qquad I_{\mathrm{Na}} \qquad V_{\mathrm{m}}

(in the latter case, "m" is short for "membrane", and so is descriptive).
This is particularly important when using acronyms or entire words as subscripts,
because otherwise LaTeX treats the letters as a sequence of variables multiplied together,
and puts too much space between them, e.g.:

.. math::

    E_{NMDA}

The reason this rule is so often broken is that by default :math:`\LaTeX` assumes a subscript is a variable:

.. class:: center

    ``V_m`` ➜ :math:`V_m`

To typeset the subscript in a roman/upright type requires something like:

.. class:: center

    ``V_{\\mathrm{m}}`` ➜ :math:`V_{\mathrm{m}}`

(There are several ways to do this. I usually use ``\\mathrm``.
This `StackExchange article`_ has a nice discussion of alternative approaches.)


Units and physical quantities
-----------------------------

Here the basic rules are:

1. units should always be in roman (upright) type;
2. for quantities there should always be a space between the number and the unit.

For more detailed rules, see the NIST `Guide for the Use of the International System of Units`_.

When writing in :math:`\LaTeX` I usually use a thin space, ``\,``, e.g.:

.. class:: center

    ``250\,\mathrm{pS/cm^{2}}`` ➜ :math:`250\,\mathrm{pS/cm^{2}}`


but this is a stylistic choice, a full space is also fine; publishers may have their own style guides for this.

.. class:: center

    ``250~\mathrm{pS/cm^{2}}`` ➜ :math:`250~\mathrm{pS/cm^{2}}`

(Note also the use of ``~`` for the full space; this prevents the number and units being separated by a line break.)

Alternaively, the :math:`\LaTeX` siunitx_ package provides a nice set of tools for consistent typesetting of quantities, e.g.:

..  code-block:: latex

   \usepackage{siunitx}

   \qty{250}{pS/cm^2}
   \qty{250}{\pico\siemens\per\square\cm}

I should probably switch to using this myself, but old habits die hard.

Conclusion
----------

In summary, please typeset your subscripts and quantities properly.
It will soothe my pedantic brain and make it much easier for me to focus on what really matters,
the content of what you have to say!

.. _`Please Make A Note blog`: http://pleasemakeanote.blogspot.com/2010/07/italics-in-math-equations.html
.. _`"Typefaces"`: https://physics.nist.gov/cuu/pdf/typefaces.pdf
.. _`ISO 80000 standard`: https://www.iso.org/obp/ui/#iso:std:iso:80000:-2:ed-2:v2:en
.. _`StackExchange article`: https://tex.stackexchange.com/questions/98406/which-command-should-i-use-for-textual-subscripts-in-math-mode
.. _`Guide for the Use of the International System of Units`: https://physics.nist.gov/cuu/pdf/sp811.pdf
.. _siunitx: https://ctan.org/pkg/siunitx
