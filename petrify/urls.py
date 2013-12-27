# coding=utf-8

import os
from django.conf import settings
from django.conf.urls import url, patterns
from django.core.urlresolvers import reverse
from petrify.models import EntityUniverse
from petrify.views import view_entity, view_page


def get_entities_urls():
    for collection in EntityUniverse().get_all_collections():
        for entity in collection.get_all():
            yield entity.get_absolute_url()


def get_pages_urls():
    pages_dir = settings.PETRIFY_PAGES_DIR
    for dirpath, dirnames, filenames in os.walk(pages_dir):
        relative_dirpath = dirpath[len(pages_dir):]
        for filename in filenames:
            yield reverse('page', args=[os.path.join(relative_dirpath, filename)])


def get_url_patterns():
    urlpatterns = patterns('')
    for entity_type, collection_type in settings.PETRIFY_ENTITIES_MAP.items():
        urlpatterns.append(
            url(r'^' + collection_type + r'/(?P<slug>[^/\.]+)/$', view_entity, name=entity_type,
                kwargs={'entity_type': entity_type}))
    urlpatterns.append(url(r'^(?P<path>.*)$', view_page, name='page'))
    return urlpatterns
