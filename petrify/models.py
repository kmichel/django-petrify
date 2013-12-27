# coding=utf-8

import datetime
import markdown2
import os
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import Context, Template
from django.utils.safestring import mark_safe


class Entity(object):
    def __init__(self, universe, entity_type, slug, filename):
        self.universe = universe
        self.type = entity_type
        self.slug = slug
        self.filename = filename

    def get_raw_attributes(self):
        with open(self.filename) as source_file:
            template = Template(source_file.read())
        markdown_text = template.render(Context())
        html = markdown2.markdown(markdown_text, extras=['metadata'])
        attributes = html.metadata
        attributes['content'] = html
        return attributes

    def get_attribute(self, key):
        # Cache point
        if self.universe.is_collection_type(key):
            return self.universe.get_collection(key).filter(lambda entity: entity.get_attribute(self.type) == self)
        elif self.universe.is_entity_type(key):
            return self.universe.get_entity(key, self.get_raw_attributes()[key])
        elif key == 'date':
            return datetime.datetime.strptime(self.get_raw_attributes()['date'], '%d-%m-%Y')
        elif key == 'content':
            content = self.get_raw_attributes()['content']
            return mark_safe(content if content != '<p></p>\n' else '')
        elif key == 'slug':
            return self.slug
        else:
            attributes = self.get_raw_attributes()
            if key in attributes:
                return attributes[key]
            else:
                raise KeyError(key)

    def __getitem__(self, item):
        if isinstance(item, int):
            raise KeyError(item)
        return self.get_attribute(item)

    def __eq__(self, other):
        return self.universe == other.universe and self.type == other.type and self.slug == other.slug

    def get_absolute_url(self):
        return reverse(self.type, args=[self.slug])


class EntityCollection(object):
    def __init__(self, universe, entity_type, collection_dir):
        self.entity_type = entity_type
        self.universe = universe
        self.collection_dir = collection_dir

    def get_entity(self, slug):
        # Cache point
        return Entity(self.universe, self.entity_type, slug, self._get_entity_filename(slug))

    def get_all(self):
        for entry_name in os.listdir(self.collection_dir):
            slug, extension = os.path.splitext(entry_name)
            if extension == '.md':
                yield self.get_entity(slug)

    def filter(self, assertion):
        return EntitySubCollection(self, assertion)

    def _get_entity_filename(self, slug):
        return os.path.join(self.collection_dir, slug + '.md')


class EntitySubCollection(object):
    def __init__(self, collection, assertion):
        self.collection = collection
        self.assertion = assertion

    def get_entity(self, slug):
        entity = self.collection.get_entity(slug)
        if entity and self.assertion(entity):
            return entity

    def get_all(self):
        return [entity for entity in self.collection.get_all() if self.assertion(entity)]


class EntityUniverse(object):
    def get_entity(self, entity_type, slug):
        return self.get_collection(self.get_collection_type(entity_type)).get_entity(slug)

    def get_collection(self, collection_type):
        # Cache point
        return EntityCollection(self, self.get_entity_type(collection_type), self.get_collection_dir(collection_type))

    def get_all_collections(self):
        for collection_type in settings.PETRIFY_ENTITIES_MAP.values():
            yield self.get_collection(collection_type)

    def get_collection_dir(self, collection_type):
        return os.path.join(settings.PETRIFY_ENTITIES_DIR, collection_type)

    def get_collection_type(self, entity_type):
        return settings.PETRIFY_ENTITIES_MAP[entity_type]

    def get_entity_type(self, collection_type):
        for key, value in settings.PETRIFY_ENTITIES_MAP.items():
            if value == collection_type:
                return key

    def is_collection_type(selfl, collection_type):
        return collection_type in settings.PETRIFY_ENTITIES_MAP.values()

    def is_entity_type(self, entity_type):
        return entity_type in settings.PETRIFY_ENTITIES_MAP.keys()

    def __getitem__(self, item):
        if isinstance(item, int):
            raise KeyError(item)
        return self.get_collection(item)
