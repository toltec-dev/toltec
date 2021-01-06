======
Toltec
======

.. class:: center

a community-maintained repository of free software for the reMarkable tablet.

Install Toltec
==============

::

    $ wget http://toltec-dev.org/bootstrap
    $ echo "cbe83d1ae2d3ef6291a2b57202bb59aace14f2f1849bbdb09552a7419995294a  bootstrap" | sha256sum -c
    $ bash bootstrap

.. class:: left

  To automatically install Toltec, run the bootstrap script in a SSH session on your reMarkable

.. class:: right

  This script installs the toltec package repository and `related tools <#>`_.


What does Toltec do?
====================

.. class:: left

  Toltec is a repository of homebrew applications for the remarkable tablet, similar to homebrew for Mac or linux package repositories.


.. class:: right

::

     $ opkg install nao


How to use
==========

.. class:: left

  the `opkg` command is used to add/remove/update packages. `see our quickstart guide <#>`_


.. class:: right

::

     $ opkg update
     $ opkg upgrade


---------------------------------------------------------------

Frequently Asked Questions
==========================

* Where can I see all the packages available?

  at https://toltec-dev.org/stable

* Do you support reMarkable 2?

  Yes, but you need to install the rm2fb package if you want to use any applications that use the display.

* Is this supported by reMarkable AS?

  No, it is a community project

* Where can I get help?

  `please open an issue on github <#>`_

* Will this brick my remarkable?

  No
