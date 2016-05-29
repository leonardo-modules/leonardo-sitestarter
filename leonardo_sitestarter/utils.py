
import yaml

from collections import OrderedDict


class Loader(yaml.Loader):

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)
        self.add_constructor(
            'tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor(
            'tag:yaml.org,2002:omap', type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructError(None, None,
                                                  'expected a mapping node, but found %s' % node.id,
                                                  node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as err:
                raise yaml.constructor.ConstructError(
                    'while constructing a mapping', node.start_mark,
                    'found unacceptable key (%s)' % err, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping


def _load_from_stream(stream):
    result = None
    try:
        result = yaml.load(stream, Loader=Loader)
    except:
        pass
    else:
        return result
    try:
        import json
        result = json.load(stream)
    except:
        pass
    else:
        return result

    if not result:
        raise Exception('cannot load the stream %s' % stream)
    return result


def _get_item(model, value, identifier=None):
    '''returns item or raise exception
    support value=first,last
    '''

    try:

        if value == "__first__":
            return model.objects.first()
        if value == "__last__":
            return model.objects.last()

        if str(value).isdigit() and not identifier:
            identifier = 'id'
        return model.objects.get(**{identifier: value})

    except model.DoesNotExist:
        raise Exception('The %s %s:%s not found.' % (model, identifier, value))
