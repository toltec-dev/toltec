======
Toltec
======

.. class:: center

A community-maintained repository of free software for the reMarkable tablet.

.. image:: ./logo.png
  :height: 400
  :class: logo


Install Toltec
==============


To install Toltec, paste the following lines in `a SSH session
<https://remarkablewiki.com/tech/ssh>`_ on your reMarkable.
This will install the Toltec package repository and related tools.

::

    $ wget http://toltec-dev.org/bootstrap
    $ echo "cbe83d1ae2d3ef6291a2b57202bb59aace14f2f1849bbdb09552a7419995294a bootstrap" | sha256sum -c
    $ bash bootstrap


What Does Toltec Do?
====================

Toltec is a repository of unofficial applications for the reMarkable tablet, similar to Homebrew for Mac or Linux.
Toltec keeps track of which apps you have installed and makes it easy to update or remove them.

.. container:: columns

    .. container::

        Use the **opkg** command to add, remove, and update packages from the command line.

    .. container::

        ::

            $ opkg update
            $ opkg upgrade
            $ opkg install <package>
            $ opkg remove <package>
            $ opkg info <package>

    .. container::

        Or install **nao** to manage packages using a graphical interface.

    .. container::

        .. image:: ./nao.png
            :width: 100%
            :class: screenshot

.. class:: center

    .. raw:: html

        <p><a class="button" href="https://toltec-dev.org/stable">Browse available packages</a></p>


Frequently Asked Questions
==========================

* Do you support reMarkable 2?

  Yes, but you need to install the rm2fb package if you want to use any applications that use the display.

* Is this supported by reMarkable AS?

  No, it is a community project

* Where can I get help?

  `please open an issue on github <#>`_

* Will this brick my remarkable?

  No, but `standard disclaimers apply <https://github.com/toltec-dev/toltec/blob/stable/LICENSE>`_
