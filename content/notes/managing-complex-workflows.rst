Managing complex workflows in neural simulation/data analysis
=============================================================

:date: 2013-07-29 10:20
:tags: reproducible research
:category: Notes
:slug: managing-complex-workflows
:author: Andrew Davison

At the `CNS 2013`_ meeting in Paris, France, Sonja Grün, Michael Denker and I gave a tutorial on managing complex workflows in neuroscience. The abstract was as follows:

*In our attempts to uncover the mechanisms that govern brain processing on the level of interacting neurons, neuroscientists have taken on the challenge of tackling the sheer complexity exhibited by neuronal networks. Neuronal simulations are nowadays performed with a high degree of detail, covering large, heterogeneous networks. Experimentally, electrophysiologists can simultaneously record from hundreds of neurons in complicated behavioral paradigms. The data streams of simulation and experiment are thus highly complex; moreover, their analysis becomes most interesting when considering their intricate correlative structure.*

*The increases in data volume, parameter complexity, and analysis difficulty represent a large burden for researchers in several respects. Experimenters, who traditionally need to cope with various sources of variability, require efficient ways to record the wealth of details of their experiment ("meta data") in a concise and machine-readable way. Moreover, to facilitate collaborations between simulation, experiment and analysis there is a need for common interfaces for data and software tool chains, and clearly defined terminologies. Most importantly, however, neuroscientists have increasing difficulties in reliably repeating previous work, one of the cornerstones of the scientific method. At first sight this ought to be an easy task in simulation or data analysis, given that computers are deterministic and do not suffer from the problems of biological variability. In practice, however, the complexity of the subject matter and the long time scales of typical projects require a level of disciplined book-keeping and detailed organization that is difficult to keep up.*

*The failure to routinely achieve replicability in computational neuroscience (probably in computational science in general, see Donoho et al., 2009 [1]) has important implications for both the credibility of the field and for its rate of progress (since reuse of existing code is fundamental to good software engineering). For individual researchers, as the example of ModelDB has shown, sharing reliable code enhances reputation and leads to increased impact.*

*In this tutorial we will identify the reasons for the difficulties often encountered in organizing and handling data, sharing work in a collaboration, and performing manageable, reproducible yet complex computational experiments and data analyses. We will also discuss best practices for making our work more reliable and more easily reproducible by ourselves and others -- without adding a huge burden to either our day-to-day research or the publication process.*

*We will cover a number of tools that can facilitate a reproducible workflow and allow tracking the provenance of results from a published article back through intermediate analysis stages to the original data, models, and/or simulations. The tools that will be covered include Git_, Mercurial_, Sumatra_, VisTrails_, odML_, Neo_. Furthermore, we will highlight strategies to validate the correctness, reliability and limits of novel concepts and codes when designing computational analysis approaches (e.g., [2-4]).*

My slides_ [pdf; 10 MB] are available under the CC-BY licence. Partial notes for the tutorial are online at http://rrcns.readthedocs.org/en/cns2013/. I hope I will have time to complete/update them later.

**References:**

1. `Donoho et al. (2009) 15 Years of Reproducible Research in Computational Harmonic Analysis, Computing in Science and Engineering 11: 8-18. doi:10.1109/MCSE.2009.15 <http://dx.doi.org/10.1109/MCSE.2009.15>`_
2. `Pazienti and Grün (2006) Robustness of the significance of spike synchrony with respect to sorting errors. Journal of Computational Neuroscience 21:329-342. <http://dx.doi.org/10.1007/s10827-006-8899-7>`_
3. Louis et al. (2010) Generation and selection of surrogate methods for correlation analysis. In: `Analysis of parallel spike trains. eds. Grün & Rotter. Springer Series in Computational Neuroscience. <http://www.springer.com/biomed/neuroscience/book/978-1-4419-5674-3>`_
4. `Louis et al. (2010) Surrogate spike train generation through dithering in operational time. Front. Comput. Neurosci. 4: 127. doi:10.3389/fncom.2010.00127 <http://dx.doi.org/10.3389/fncom.2010.00127>`_



.. _`CNS 2013`: http://www.cnsorg.org/cns-2013-paris
.. _slides: https://dl.dropboxusercontent.com/u/730085/workflows_tutorial_cns2013_davison.pdf
.. _Git: http://git-scm.com/
.. _Mercurial: http://mercurial.selenic.com/
.. _Sumatra: http://neuralensemble.org/sumatra
.. _VisTrails: http://www.vistrails.org/
.. _odML: http://www.g-node.org/projects/odml
.. _Neo: http://neuralensemble.org/neo


