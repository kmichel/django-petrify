# coding=utf-8

from django.shortcuts import render
from petrify.models import EntityUniverse


def view_page(request, path):
    # TODO: make it safe
    if not path or path.endswith('/'):
        path += 'index.html'
    return render(request, path, {})


def view_entity(request, entity_type, slug):
    universe = EntityUniverse()
    return render(request, entity_type + '.html', {entity_type: universe.get_entity(entity_type, slug)})
