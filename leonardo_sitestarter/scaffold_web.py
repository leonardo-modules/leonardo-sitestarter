
import logging
import os

import requests
import six
from collections import OrderedDict
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core import management
from horizon_contrib.common import get_class
from leonardo.models import (Page, PageColorScheme, PageTheme, WidgetBaseTheme,
                             WidgetContentTheme, WidgetDimension)

from .utils import _load_from_stream, _get_item, get_or_create

LOG = logging.getLogger('leonardo')

LEONARDO_BOOTSTRAP_DIR = getattr(settings, 'LEONARDO_BOOTSTRAP_DIR', None)
LEONARDO_FAIL_SILENTLY = getattr(settings, 'LEONARDO_FAIL_SILENTLY', False)


def get_loaded_scripts(directory=LEONARDO_BOOTSTRAP_DIR):
    """return dictionary of loaded scripts from specified directory
    """

    scripts = {}

    if not directory:
        raise Exception("You must set LEONARDO_BOOTSTRAP_DIR"
                        " absolute path to bootstrap scripts")

    for root, dirnames, filenames in os.walk(directory):

        for file_name in filenames:

            try:

                ext = file_name.split('.')[1]

                with open(os.path.join(directory, file_name), 'r') as file:

                    scripts[file_name] = _load_from_stream(file)

            except Exception as e:
                LOG.exception('Error in during loading {} file with {}'.format(
                    file_name, str(e)))

    return scripts


def _handle_regions(regions, feincms_object, fail_silently=False):

    if not feincms_object:
        LOG.warning('Skipped {}' % regions.items())
        return None

    for region, widgets in six.iteritems(regions):
        i = 0
        for widget_cls, widget_attrs in six.iteritems(widgets):

            try:
                WidgetCls = get_class(widget_cls)
            except Exception as e:
                if not fail_silently:
                    raise Exception('Cannout load {} with {}'.format(
                        widget_cls, e))

            # TODO create form and validate options
            w_attrs = widget_attrs.get('attrs', {})
            w_attrs.update({
                'parent': feincms_object,
                'region': region,
                'ordering': w_attrs.get('ordering', i)
            })

            w_attrs['content_theme'] = WidgetContentTheme.objects.get(
                name=w_attrs.get('content_theme', 'default'),
                widget_class=WidgetCls.__name__)

            w_attrs['base_theme'] = _get_item(
                WidgetBaseTheme,
                w_attrs.get('base_theme', 'default'),
                "name")

            try:
                widget = WidgetCls(**w_attrs)
                widget.save(created=False)
            except Exception as e:
                if not fail_silently:
                    raise e
                else:
                    LOG.exception(e)

            else:
                for size, width in six.iteritems(
                        widget_attrs.get('dimensions', {})):

                    WidgetDimension(**{
                        'widget_id': widget.pk,
                        'widget_type': widget.content_type,
                        'size': size,
                        'width': width
                    }).save()

                i += 1


def create_new_site(run_syncall=False, request=None,
                    name='demo.yaml', url=None, force=False):
    """load all available scripts and try scaffold new site from them

    TODO(majklk): refactor and support for more cases

    """

    if force:
        management.call_command('flush', interactive=False)

    if run_syncall:
        management.call_command('sync_all', force=True)

    if url:
        response = requests.get(url)
        if response.status_code == 404:
            raise requests.exceptions.HTTPError(url + ' not found')
        BOOTSTRAP = _load_from_stream(response.text)
    else:
        try:
            scripts = get_loaded_scripts()
            BOOTSTRAP = scripts[name]
        except KeyError:
            raise Exception('Cannot find {} in {} loaded from {}'.format(
                name, scripts, LEONARDO_BOOTSTRAP_DIR))

    return load_data(BOOTSTRAP)


def load_data(data, fail_silently=True):

    root_page = None

    for username, user_attrs in six.iteritems(data.pop('auth.User', {})):

        if not User.objects.filter(
                username=username,
                email=user_attrs['mail']).exists():

            try:
                # create and login user
                User.objects.create_superuser(
                    username, user_attrs['mail'], user_attrs['password'])
            except Exception as e:
                if not fail_silently:
                    raise e
                else:
                    LOG.exception(e)

    for page_name, page_attrs in six.iteritems(data.pop('web.Page', {})):

        page_theme_name = page_attrs.pop('theme', '__first__')
        page_color_scheme_name = page_attrs.pop('color_scheme', '__first__')

        regions = page_attrs.pop('content', {})

        if not (PageTheme.objects.exists() or
                PageColorScheme.objects.exists()):
            raise Exception(
                "You havent any themes please install someone and run sync_all")

        page_attrs['theme'] = _get_item(PageTheme, page_theme_name, "name")

        page_attrs['color_scheme'] = _get_item(PageColorScheme,
                                               page_color_scheme_name, "name")

        parent = page_attrs.get('parent', None)

        if parent:
            if str(parent).isdigit():
                page_attrs['parent'] = _get_item(Page, parent)
            else:
                page_attrs['parent'] = _get_item(Page, parent, "slug")

        page, created = get_or_create(Page, fail_silently, **page_attrs)

        # TODO from attrs etc..
        root_page = page

        _handle_regions(regions, page, fail_silently)

    # generic stuff
    for cls_name, entries in six.iteritems(data):

        for entry, cls_attrs in six.iteritems(entries):

            cls = get_class(cls_name)

            regions = cls_attrs.pop('content', {})

            # load FK from
            # author: {'pk': 1, 'type': 'auth.User'}
            for attr, value in six.iteritems(cls_attrs):
                if isinstance(value, (dict, OrderedDict)):
                    cls_type = value.get('type', None)
                    if cls_type:
                        try:
                            cls_attrs[attr] = _get_item(get_class(
                                cls_type), value.get('pk'))
                        except Exception as e:
                            if not fail_silently:
                                raise Exception(
                                    'Cannot load FK {} not Found original exception {}'.format(cls_type, e))

            instance, created = get_or_create(cls, fail_silently, **cls_attrs)

            _handle_regions(regions, instance, fail_silently)

    return root_page
