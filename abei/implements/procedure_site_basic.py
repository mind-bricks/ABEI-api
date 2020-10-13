from abei.interfaces import (
    IProcedure,
    IProcedureSite,
    IProcedureSiteFactory,
    IProcedureDataFactory,
    IProcedureFactory,
    service_entry as _
)
from abei.implements.util import LazyProperty


class ProcedureSiteBasic(IProcedureSite):

    def __init__(self, procedure_sites=None):
        self.procedure_sites = procedure_sites or []
        self.procedures = {}

    def get_procedure(self, signature, **kwargs):
        procedure = self.query_procedure(signature, **kwargs)
        if not procedure:
            raise LookupError('procedure not found')
        return procedure

    def query_procedure(self, signature, depth=-1, **kwargs):
        procedure = self.procedures.get(str(signature))
        if procedure:
            return procedure

        if depth == 0:
            return None

        # try to find in dependent sites
        for s in self.procedure_sites:
            procedure = s.query_procedure(
                signature, depth=depth - 1, **kwargs)
            if procedure:
                return procedure

        return None

    def register_procedure(self, procedure, **kwargs):
        assert isinstance(procedure, IProcedure)
        signature = str(procedure.get_signature())
        if not kwargs.get('overwrite') and self.query_procedure(signature):
            raise AssertionError('procedure already registered')

        self.procedures[signature] = procedure
        return procedure

    def iterate_procedures(self):
        return self.procedures.keys()

    def get_base_sites(self):
        return self.procedure_sites


class ProcedureSiteFactory(IProcedureSiteFactory):

    def __init__(self, service_site, **kwargs):
        self.service_site = service_site

    @LazyProperty
    def builtin_site(self):
        service = self.service_site.get_service(_(IProcedureFactory))
        service_d = self.service_site.get_service(_(IProcedureDataFactory))

        class_bool = service_d.get_class('bool@py')
        class_int = service_d.get_class('int@py')
        class_float = service_d.get_class('float@py')
        class_string = service_d.get_class('string@py')

        site = ProcedureSiteBasic()
        for p in [
            service.create('probe@py', data_class=class_bool),
            service.create('not@py', data_class=class_bool),
            service.create('and@py', data_class=class_bool),
            service.create('or@py', data_class=class_bool),

            service.create('probe@py', data_class=class_int),
            service.create('neg@py', data_class=class_int),
            service.create('sq@py', data_class=class_int),
            service.create('add@py', data_class=class_int),
            service.create('sub@py', data_class=class_int),
            service.create('mul@py', data_class=class_int),
            service.create('mod@py', data_class=class_int),
            service.create('mod_div@py', data_class=class_int),
            service.create('pow@py', data_class=class_int),
            service.create('eq@py', data_class=class_int),
            service.create('ne@py', data_class=class_int),
            service.create('lt@py', data_class=class_int),
            service.create('lte@py', data_class=class_int),
            service.create('gt@py', data_class=class_int),
            service.create('gte@py', data_class=class_int),
            service.create('diverge2@py', data_class=class_int),
            service.create('converge2@py', data_class=class_int),

            service.create('probe@py', data_class=class_float),
            service.create('neg@py', data_class=class_float),
            service.create('sq@py', data_class=class_float),
            service.create('add@py', data_class=class_float),
            service.create('sub@py', data_class=class_float),
            service.create('mul@py', data_class=class_float),
            service.create('div@py', data_class=class_float),
            service.create('mod@py', data_class=class_float),
            service.create('mod_div@py', data_class=class_float),
            service.create('pow@py', data_class=class_float),
            service.create('eq@py', data_class=class_float),
            service.create('ne@py', data_class=class_float),
            service.create('lt@py', data_class=class_float),
            service.create('lte@py', data_class=class_float),
            service.create('gt@py', data_class=class_float),
            service.create('gte@py', data_class=class_float),
            service.create('diverge2@py', data_class=class_float),
            service.create('converge2@py', data_class=class_float),

            service.create('probe@py', data_class=class_string),
            service.create('add@py', data_class=class_string),
            service.create('eq@py', data_class=class_string),
            service.create('ne@py', data_class=class_string),
            service.create('diverge2@py', data_class=class_string),
            service.create('converge2@py', data_class=class_string),
        ]:
            site.register_procedure(p)
        return site

    def create(self, procedure_sites, builtin=False, **kwargs):
        assert not (procedure_sites and builtin)

        return self.builtin_site if builtin else ProcedureSiteBasic(
            procedure_sites=procedure_sites or [self.builtin_site])
