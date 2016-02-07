
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

note: be sure that you have synced templates and collected & compressed static files.

Settings
--------

.. code-block:: bash

    # default
    LEONARDO_BOOTSTRAP_URL = 'http://github.com/django-leonardo/django-leonardo/raw/master/contrib/bootstrap/demo.yaml'

    LEONARDO_BOOTSTRAP_DIR = '/srv/leonardo'
    
    ls /srv/leonardo
    demo.yml

Example
-------

.. code-block:: yaml

    auth.User:
      admin:
        password: root
        mail: root@admin.cz
    web.Page:
      QuickStart:
        title: Quickstart
        slug: quickstart
        override_url: /
        featured: false
        theme: bootstrap
        in_navigation: true
        active: true
        color_scheme: default
        content:
          header:
            web.SiteHeadingWidget:
              attrs:
                site_title: Leonardo Site
                content_theme: navbar
                base_theme: default
              dimenssions:
                md: 2

Commands
--------

Bootstraping site is kicked of by middleware in default state, but if you want bootstrap manualy and then uninstall this plugin you can do this::

    python manage.py bootstrap_site demo

    python manage.py bootstrap_site --url=https://raw.githubusercontent.com/django-leonardo/django-leonardo/master/contrib/bootstrap/blog.yaml


Read More
=========

* https://github.com/django-leonardo/django-leonardo
