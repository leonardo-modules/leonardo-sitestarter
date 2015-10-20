
=============================
Leonardo leonardo-sitestarter
=============================

Simple leonardo utility for generating Leonardo Sites from templates declared in yaml or json localy or on remote storage.

.. contents::
    :local:

Installation
------------

.. code-block:: bash

    pip install leonardo-sitestarter


Settings
--------

.. code-block:: bash

    LEONARDO_BOOTSTRAP_DIR = '/srv/leonardo'
    
    ls /srv/leonardo
    demo.yml

Commands
--------

Bootstraping site is kicked of by middleware in default state, but if you want bootstrap manualy and then uninstall this plugin you can do this::

    python manage.py bootstrap_site demo

    python manage.py bootstrap_site --url=https://raw.githubusercontent.com/django-leonardo/django-leonardo/master/contrib/bootstrap/blog.yaml


Read More
=========

* https://github.com/django-leonardo/django-leonardo
