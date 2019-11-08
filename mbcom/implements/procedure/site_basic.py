from mbcom.interfaces import (
    IProcedure,
    IProcedureSite,
    IProcedureSiteFactory,
    IProcedureFactory,
    service_entry as _
)


class ProcedureSiteBasic(IProcedureSite):

    def __init__(self):
        self.procedures = {}

    def get_procedure(self, signature):
        procedure = self.query_procedure(signature)
        if not procedure:
            raise LookupError('procedure not found')
        return procedure

    def query_procedure(self, signature):
        return self.procedures.get(str(signature))

    def register_procedure(self, procedure, **kwargs):
        assert isinstance(procedure, IProcedure)
        signature = str(procedure.get_signature())
        if not kwargs.get('overwrite') and self.query_procedure(signature):
            raise AssertionError('procedure already registered')

        self.procedures[signature] = procedure
        return procedure

    def get_dependencies(self):
        return []


class ProcedureSiteFactoryBasic(IProcedureSiteFactory):

    def __init__(self, service_site, **kwargs):
        self.factory = service_site.get_service(_(IProcedureFactory))

    def create_builtin_site(self):
        service = self.factory
        site = ProcedureSiteBasic()
        for p in [
            service.create('not@py', 'bool@py'),
            service.create('and@py', 'bool@py'),
            service.create('or@py', 'bool@py'),

            service.create('neg@py', 'int@py'),
            service.create('sq@py', 'int@py'),
            service.create('add@py', 'int@py'),
            service.create('sub@py', 'int@py'),
            service.create('mul@py', 'int@py'),
            service.create('mod@py', 'int@py'),
            service.create('mod_div@py', 'int@py'),
            service.create('pow@py', 'int@py'),
            service.create('eq@py', 'int@py'),
            service.create('ne@py', 'int@py'),
            service.create('lt@py', 'int@py'),
            service.create('lte@py', 'int@py'),
            service.create('gt@py', 'int@py'),
            service.create('gte@py', 'int@py'),
            service.create('branch@py', 'int@py'),

            service.create('neg@py', 'float@py'),
            service.create('sq@py', 'float@py'),
            service.create('add@py', 'float@py'),
            service.create('sub@py', 'float@py'),
            service.create('mul@py', 'float@py'),
            service.create('div@py', 'float@py'),
            service.create('mod@py', 'float@py'),
            service.create('mod_div@py', 'float@py'),
            service.create('pow@py', 'float@py'),
            service.create('eq@py', 'float@py'),
            service.create('ne@py', 'float@py'),
            service.create('lt@py', 'float@py'),
            service.create('lte@py', 'float@py'),
            service.create('gt@py', 'float@py'),
            service.create('gte@py', 'float@py'),
            service.create('branch@py', 'float@py'),

            service.create('add@py', 'string@py'),
            service.create('eq@py', 'string@py'),
            service.create('ne@py', 'string@py'),
            service.create('branch@py', 'string@py'),
        ]:
            site.register_procedure(p)
        return site

    def create(self, procedure_sites, **kwargs):
        return self.create_builtin_site()
