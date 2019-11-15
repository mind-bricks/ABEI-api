from abei.interfaces import (
    IProcedure,
    IProcedureSite,
    IProcedureSiteFactory,
    IProcedureFactory,
    service_entry as _
)
from ..util import LazyProperty


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


class ProcedureSiteFactoryBasic(IProcedureSiteFactory):

    def __init__(self, service_site, **kwargs):
        self.service_site = service_site

    @LazyProperty
    def builtin_site(self):
        service = self.service_site.get_service(_(IProcedureFactory))
        site = ProcedureSiteBasic()
        for p in [
            service.create('not@py', data_signature='bool@py'),
            service.create('and@py', data_signature='bool@py'),
            service.create('or@py', data_signature='bool@py'),

            service.create('neg@py', data_signature='int@py'),
            service.create('sq@py', data_signature='int@py'),
            service.create('add@py', data_signature='int@py'),
            service.create('sub@py', data_signature='int@py'),
            service.create('mul@py', data_signature='int@py'),
            service.create('mod@py', data_signature='int@py'),
            service.create('mod_div@py', data_signature='int@py'),
            service.create('pow@py', data_signature='int@py'),
            service.create('eq@py', data_signature='int@py'),
            service.create('ne@py', data_signature='int@py'),
            service.create('lt@py', data_signature='int@py'),
            service.create('lte@py', data_signature='int@py'),
            service.create('gt@py', data_signature='int@py'),
            service.create('gte@py', data_signature='int@py'),
            service.create('switch@py', data_signature='int@py'),

            service.create('neg@py', data_signature='float@py'),
            service.create('sq@py', data_signature='float@py'),
            service.create('add@py', data_signature='float@py'),
            service.create('sub@py', data_signature='float@py'),
            service.create('mul@py', data_signature='float@py'),
            service.create('div@py', data_signature='float@py'),
            service.create('mod@py', data_signature='float@py'),
            service.create('mod_div@py', data_signature='float@py'),
            service.create('pow@py', data_signature='float@py'),
            service.create('eq@py', data_signature='float@py'),
            service.create('ne@py', data_signature='float@py'),
            service.create('lt@py', data_signature='float@py'),
            service.create('lte@py', data_signature='float@py'),
            service.create('gt@py', data_signature='float@py'),
            service.create('gte@py', data_signature='float@py'),
            service.create('switch@py', data_signature='float@py'),

            service.create('add@py', data_signature='string@py'),
            service.create('eq@py', data_signature='string@py'),
            service.create('ne@py', data_signature='string@py'),
            service.create('switch@py', data_signature='string@py'),
        ]:
            site.register_procedure(p)
        return site

    def create(self, procedure_sites, **kwargs):
        return ProcedureSiteBasic(
            procedure_sites=procedure_sites or [self.builtin_site])
