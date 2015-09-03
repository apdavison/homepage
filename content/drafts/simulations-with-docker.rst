Neuronal network simulations with Docker
========================================

:date: 2015-08-26
:tags: Python, NEURON, NEST, PyNN, Docker
:category: Notes
:slug: simulations-with-docker
:author: Andrew Davison

There has been a lot of discussion of using Docker_ containers to improve the
reproducibility of computational research. See, for example, ...

fans
  http://arxiv.org/abs/1410.0846
  http://melissagymrek.com/science/2014/08/29/docker-reproducible-research.html
not fans
  http://ivory.idyll.org/blog/2014-containers.html
  https://blog.wearewizards.io/why-docker-is-not-the-answer-to-reproducible-research-and-why-nix-may-be


This post, however, is not about reproducibility so much as convenience, although improved
reproducibility will surely come as a side-effect.
Running simulations in a Docker container provides two important advantages, which promise to
save me a lot of time:

    1. **portability/consistency**. Once I have a Docker image into which all of the libraries I
       need have been installed, setting up my work environment on a new machine, or creating a
       work environment for a new student, is a single command, and takes a few minutes (the
       time to download the image from the `Docker Hub`_), rather than the hour or so (or
       several days for new student wrestling with version incompatibilities) is takes me to
       do it manually. Furthermore, I now have an identical environment on all machines, which
       may be less than ideal for developing robust libraries, but is great for getting some
       science done.

    2. **running Linux simulations on OS X**. Many of the simulators I use (NEST_, NEURON_), and
       some of the Python packages (e.g. NumPy_), have a lot of C/C++ code. Over the time that
       I've used Mac OS X (from 10.4 to 10.10), getting everything to build has varied
       non-monotonically between straightforward, fiddly and near impossible. Conda_ has
       greatly simplified installation of the general scientific Python stack, but it is still a
       time-consuming adventure to re-install everything each time a new version of OS X or NEST
       is released. For some time now, I've been side-stepping the problems when in the
       "near impossible" condition by using virtual Linux machines running in VMWare_ or
       VirtualBox_. Manually installing a new VM from an .iso file and configuring shared folders,
       etc., is itself a time consuming process. I tried Vagrant_ as a way to simplify and
       automate VM construction, and I still think Vagrant is an excellent solution to most of
       these problems, but then I tried Docker and for reasons I haven't yet thought through, I
       stuck with that.


Getting started
---------------

The Docker website has clear instructions on installing the software and getting up and running
(instructions for `Mac OS X`_, Linux_ and Windows_).
Assuming that you have everything up and running, you can start running simulations with NEST,
NEURON, Brian_ and PyNN_ as follows:

    docker run -i -t neuralensemble/simulation /bin/bash

This will download the `neuralensemble/simulation`_ image from the `Docker Hub`_, launch a
container, and start a shell running in the container. Note that the Dockerfile used to build
the image is here_ on Github.






    docker run -i -t -v /Users/andrew/dev/mozaik-contrib:/home/docker/dev/mozaik-contrib mozaik /bin/bash



    ssh-keygen -C docker -f ./id_rsa

    docker run -d -p 22 -v /Users/andrew/dev/mozaik-contrib:/home/docker/dev/mozaik-contrib withssh

    ssh -i ./id_rsa -p 32771 docker@192.168.99.100

cleanup

    docker rm $(docker ps -a -q)

.. _Docker: https://www.docker.com
.. _`Docker Index`: xxx
.. _NEST: xxx
.. _NEURON: xxx
.. _NumPy: xxx
.. _Conda: xxx
.. _VMWare: xxx
.. _VirtualBox: xxx
.. _Vagrant: https://www.vagrantup.com
.. _`Mac OS X`: http://docs.docker.com/mac/started/
.. _Linux: http://docs.docker.com/linux/started
.. _Windows: http://docs.docker.com/windows/started
.. _here: https://github/NeuralEnsemble/neuralensemble-docker/