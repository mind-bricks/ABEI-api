from mbcom.interfaces import (
    IProcedure,
    IProcedureSite,
    IProcedureFactory,
    service_entry as _
)


class ProcedureSiteBasic(IProcedureSite):

    def __init__(self, service_site, **kwargs):
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
        name = str(procedure.get_signature())
        if kwargs.get('overwrite'):
            assert name not in self.procedures, 'procedure already registered'

        self.procedures[name] = procedure
        return procedure


class ProcedureSiteBuiltin(IProcedureSite):
    def __init__(self, service_site, **kwargs):
        service = service_site.get_service(_(IProcedureFactory))
        self.procedures = {p.get_signature(): p for p in [
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
        ]}

    def get_procedure(self, signature):
        procedure = self.query_procedure(signature)
        if not procedure:
            raise LookupError('procedure not found')
        return procedure

    def query_procedure(self, signature):
        return self.procedures.get(str(signature))

    def register_procedure(self, procedure, **kwargs):
        raise AssertionError('not allowed to register in builtin site')
