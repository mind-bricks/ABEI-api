from mbcom.interfaces import (
    IProcedureData,
    IProcedureDataFactory,
)


class ProcedureDataBasic(IProcedureData):
    signature = 'none@py'
    label = 'none'
    value_type = type(None)
    value = None

    def clone(self):
        instance = self.__class__()
        instance.value = self.value
        return instance

    def get_signature(self):
        return self.signature

    def get_label(self):
        return self.label

    def get_value(self):
        return self.value

    def set_value(self, value):
        if not isinstance(value, self.value_type):
            raise TypeError(
                'incorrect value type of procedure data')
        self.value = value


class ProcedureDataBool(ProcedureDataBasic):
    signature = 'bool@py'
    label = 'bool'
    value_type = bool
    value = True


class ProcedureDataInt(ProcedureDataBasic):
    signature = 'int@py'
    label = 'int'
    value_type = int
    value = 0


class ProcedureDataFloat(ProcedureDataBasic):
    signature = 'float@py'
    label = 'float'
    value_type = float
    value = 0.0


class ProcedureDataString(ProcedureDataBasic):
    signature = 'string@py'
    label = 'string'
    value_type = str
    value = ''


class ProcedureDataFactoryBuiltin(IProcedureDataFactory):
    def __init__(self, service_site, **kwargs):
        self.data_classes = dict([
            (ProcedureDataBool.signature, ProcedureDataBool),
            (ProcedureDataInt.signature, ProcedureDataInt),
            (ProcedureDataFloat.signature, ProcedureDataFloat),
            (ProcedureDataString.signature, ProcedureDataString),
        ])

    def create(self, signature, *args, **kwargs):
        data_class = self.data_classes.get(signature)
        return data_class and data_class(*args, **kwargs)
