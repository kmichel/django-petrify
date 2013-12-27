#!/usr/bin/env python
# coding=utf-8

import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.urlresolvers import set_script_prefix
from django.test import Client
from petrify.urls import get_pages_urls, get_entities_urls


class Command(BaseCommand):
    help = 'export pages'

    def handle(self, *args, **options):
        script_prefix = settings.PETRIFY_EXPORT_URL
        old_static_url = settings.STATIC_URL
        try:
            settings.STATIC_URL = script_prefix[:-1] + settings.STATIC_URL
            set_script_prefix(script_prefix)
            client = Client()
            for url in get_pages_urls():
                export_url(client, url[len(script_prefix) - 1:])
            for url in get_entities_urls():
                export_url(client, url[len(script_prefix) - 1:])
        finally:
            settings.STATIC_URL = old_static_url


def export_url(client, url):
    filepath = settings.PETRIFY_EXPORT_DIR + url_to_filepath(url)
    response = client.get(url)
    create_required_dirs(filepath)
    with open(filepath, 'w') as output_file:
        output_file.write(response.content)


def url_to_filepath(url):
    if url.endswith('/'):
        return url + 'index.html'
    return url


def create_required_dirs(filepath):
    if not os.path.exists(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
