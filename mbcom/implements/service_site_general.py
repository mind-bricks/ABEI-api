from importlib import import_module

from mbcom.interfaces import (
    IServiceSite,
    IServiceConfiguration,
    ServiceEntry,
)
from .service_basic import ServiceBasic


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class
    designated by the last name in the path.
    Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        msg = '%s doesn\'t look like a module path' % dotted_path
        raise ImportError(msg)

    module = import_module(module_path)

    try:

        return getattr(module, class_name)
    except AttributeError:
        msg = 'Module "%s" does not define a "%s" attribute/class' % (
            module_path, class_name)
        raise ImportError(msg)


class ServiceSite(IServiceSite):

    def __init__(self):
        self.service_mapping = {}

    def get_service(self, entry):
        service = self.query_service(entry)
        if not service:
            raise LookupError('service not found')
        return service

    def query_service(self, entry):
        service = self.service_mapping.get(entry.interface)
        return service and service.get(entry.name)

    def register_service(self, entries, service_class, **kwargs):
        assert isinstance(entries, (tuple, list))
        # ensure dependencies first
        service_class.ensure_dependencies()
        # create service instance
        service = service_class(self, **kwargs)
        for e in entries:
            if (
                    not isinstance(e, ServiceEntry) or
                    not issubclass(service_class, e.interface)
            ):
                raise ValueError(
                    'incorrect service entries for service classes')

            self.service_mapping.setdefault(
                e.interface, {}).update({e.name: service})

        return service


class ServiceConfiguration(ServiceBasic, IServiceConfiguration):

    @classmethod
    def get_dependencies(cls):
        return ['PyYAML']

    @staticmethod
    def config_parse(parser, file_or_filename):
        if isinstance(file_or_filename, str):
            with open(file_or_filename, 'r') as f:
                return parser(f)
        else:
            return parser(file_or_filename)

    @staticmethod
    def config_process(service_site, configuration):
        if not isinstance(configuration, (tuple, list)):
            raise ValueError('invalid service configuration file')

        for config_item in configuration:
            service_class_name = config_item.pop('class', '')
            service_entries_name = config_item.pop('entries', [])
            if not isinstance(service_entries_name, (tuple, list)):
                raise ValueError(
                    'invalid service entries in configuration file')
            try:
                service_class = import_string(service_class_name)
            except ImportError:
                raise ValueError(
                    'invalid service class {}'.format(service_class_name))

            service_entries = []
            for e in service_entries_name:
                if not isinstance(e, dict):
                    raise ValueError(
                        'invalid service entry in configuration file')

                service_name = e.get('name', '')
                service_interface_name = e.get('interface', '')
                try:
                    service_interface = import_string(service_interface_name)
                except ImportError:
                    raise ValueError('invalid service interface {}'.format(
                        service_interface_name))
                service_entries.append(ServiceEntry(
                    service_interface, service_name))

            service_site.register_service(
                service_entries, service_class, **config_item)

    def load_json(self, service_site, file_or_filename):
        import json
        self.config_parse(lambda f: self.config_process(
            service_site, json.loads(f.read())), file_or_filename)

    def save_json(self, service_site, file_or_filename):
        raise NotImplementedError

    def load_yaml(self, service_site, file_or_filename):
        import yaml
        self.config_parse(lambda f: self.config_process(
            service_site, yaml.safe_load(f)), file_or_filename)

    def save_yaml(self, service_site, file_or_filename):
        raise NotImplementedError
