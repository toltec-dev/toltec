.. include:: defs.rst

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

.. parsed-literal::

    $ wget \http://toltec-dev.org/bootstrap
    $ echo "|bootstrap-hash|  bootstrap" | sha256sum -c && bash bootstrap


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

        <p><a class="button" href="stable">Browse available packages</a></p>


Frequently Asked Questions
==========================

* Do you support reMarkable 2?

  Yes, but you need to install the **rm2fb** package if you want to use any applications that interact with the display.

* Is this supported by reMarkable AS?

  No, it is a community project.

* Will this brick my reMarkable?

  Probably not, but `standard disclaimers apply <https://github.com/toltec-dev/toltec/blob/stable/LICENSE>`_.

* Where can I get help?

  If you need help with Toltec or one of its packages, feel free to join the `reMarkable community on Discord <https://discord.gg/ATqQGfu>`_.
  Please do not open issues on GitHub to ask for help, as they’re not the best medium to provide assistance.

* Can you add `_____` to Toltec?

  We’re always open to adding new packages to the repository.
  You’ll find information about how to request a package in our `contributing guide <https://github.com/toltec-dev/toltec/blob/stable/docs/contributing.md>`_.

* I found a vulnerability in Toltec or one of its packages, where can I report it?

  To inform the Toltec maintainers about a security issue, please follow the `security instructions <https://github.com/toltec-dev/organization/blob/main/docs/security.md>`_.
