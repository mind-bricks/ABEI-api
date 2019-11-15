from base64 import urlsafe_b64encode
from uuid import uuid1

from abei.interfaces import (
    IProcedure,
    IProcedureData,
    IProcedureFactory,
    IProcedureDetail,
)

from .data_basic import (
    ProcedureDataBasic,
    ProcedureDataBool,
)
from .joint_basic import (
    joint_validate,
    joint_run,
)


class ProcedureBasic(IProcedure):
    signature = 'do_nothing@py'
    docstring = ''
    input_signatures = []
    output_signatures = []

    def get_signature(self):
        return self.signature

    def get_input_signatures(self):
        return self.input_signatures

    def get_output_signatures(self):
        return self.output_signatures

    def get_docstring(self):
        return self.docstring

    def set_docstring(self, docstring):
        self.docstring = docstring

    def run(self, procedure_data_list, **kwargs):
        # assert isinstance(kwargs.setdefault('procedure_cache', {}), dict)
        return (
            self.run_normally(procedure_data_list, **kwargs) if
            self.run_input_check(
                procedure_data_list, self.input_signatures) else
            self.run_exceptionally(procedure_data_list, **kwargs)
        )

    @staticmethod
    def run_input_check(procedure_data_list, signatures):
        if len(procedure_data_list) != len(signatures):
            raise AssertionError('invalid data list')

        has_missing_params = False
        for d, sig in zip(procedure_data_list, signatures):
            if d is None:
                has_missing_params = True
                continue
            if not isinstance(d, IProcedureData):
                raise AssertionError('invalid data list')
            if d.get_signature() != sig:
                raise AssertionError('data signature miss match')

        return not has_missing_params

    def run_normally(self, procedure_data_list, **kwargs):
        return [None] * len(self.output_signatures)

    def run_exceptionally(self, procedure_data_list, **kwargs):
        return [None] * len(self.output_signatures)


class ProcedureComposite(IProcedureDetail, ProcedureBasic):
    name = 'composite@py'
    output_joints = []
    output_indices = []

    def __init__(
            self,
            signature=None,
            docstring=None,
            input_signatures=None,
            output_signatures=None,
    ):
        self.signature = signature or urlsafe_b64encode(
            uuid1().bytes).strip(b'=').decode('utf8')
        self.docstring = docstring or self.docstring
        self.input_signatures = input_signatures or self.input_signatures
        self.output_signatures = output_signatures or self.output_signatures

    def get_joints(self):
        return [(f, i) for f, i in zip(
            self.output_joints, self.output_indices)]

    def set_joints(self, joints, indices):
        joint_validate(
            joints,
            indices,
            self,
            self.output_signatures,
        )
        self.output_joints = joints
        self.output_indices = indices

    def run_normally(self, procedure_data_list, **kwargs):
        return [
            joint_run(joint, procedure_data_list, **kwargs)[i] if
            joint else procedure_data_list[i]
            for joint, i in self.get_joints()
        ]


class ProcedureBuiltin(ProcedureBasic):
    name = 'builtin_op@py'

    def __init__(self, data_signature):
        self.signature = '{}:{}'.format(data_signature, self.name)


class ProcedureUnaryOperator(ProcedureBuiltin):
    name = 'unary_op@py'
    native_function = staticmethod(lambda x: x)

    def __init__(self, data_signature=ProcedureDataBasic.signature):
        super().__init__(data_signature)
        self.input_signatures = [data_signature]
        self.output_signatures = [data_signature]

    def run_normally(self, procedure_data_list, **kwargs):
        ret = procedure_data_list[0].clone()
        ret.set_value(self.native_function(
            procedure_data_list[0].get_value()))
        return [ret]


class ProcedureBinaryOperator(ProcedureBuiltin):
    name = 'binary_op@py'
    native_function = staticmethod(lambda x, y: x)

    def __init__(self, data_signature=ProcedureDataBasic.signature):
        super().__init__(data_signature)
        self.input_signatures = [data_signature, data_signature]
        self.output_signatures = [data_signature]

    def run_normally(self, procedure_data_list, **kwargs):
        ret = procedure_data_list[0].clone()
        ret.set_value(self.native_function(
            procedure_data_list[0].get_value(),
            procedure_data_list[1].get_value(),
        ))
        return [ret]


class ProcedureComparator(ProcedureBuiltin):
    name = 'compare@py'
    native_function = staticmethod(lambda x, y: True)

    def __init__(self, data_signature=ProcedureDataBasic.signature):
        super().__init__(data_signature)
        self.input_signatures = [data_signature, data_signature]
        self.output_signatures = [data_signature]

    def run_normally(self, procedure_data_list, **kwargs):
        ret = ProcedureDataBool()
        ret.set_value(self.native_function(
            procedure_data_list[0].get_value(),
            procedure_data_list[1].get_value(),
        ))
        return [ret]


class ProcedureSwitch(ProcedureBuiltin):
    name = 'switch@py'

    def __init__(self, data_signature=ProcedureDataBasic.signature):
        super().__init__(data_signature)
        self.data_signature = data_signature
        self.input_signatures = ['bool@py', data_signature]
        self.output_signatures = [data_signature, data_signature]

    def run_normally(self, procedure_data_list, **kwargs):
        switch = procedure_data_list[0].get_value()
        ret = procedure_data_list[1].clone()
        return switch and [None, ret] or [ret, None]


class ProcedureGate(ProcedureBuiltin):
    name = 'gate@py'

    def __init__(
            self,
            data_signature=ProcedureDataBasic.signature,
            output_count=2
    ):
        super().__init__(data_signature)
        self.input_signatures = ['int@py', data_signature]
        self.output_signatures = [data_signature] * output_count

    def run_normally(self, procedure_data_list, **kwargs):
        gate = procedure_data_list[0].get_value()
        ret = procedure_data_list[1]
        return [
            (gate & (1 >> i)) and ret.clone() or None
            for i in range(len(self.output_signatures))
        ]


class ProcedureFunnel(ProcedureBuiltin):
    name = 'funnel@py'

    def __init__(
            self,
            data_signature=ProcedureDataBasic.signature,
            input_count=2
    ):
        super().__init__(data_signature)
        self.input_signatures = [data_signature] * input_count
        self.output_signatures = [data_signature]

    def run_exceptionally(self, procedure_data_list, **kwargs):
        return [next((
            data for data in procedure_data_list if
            data is not None), None
        )]


class ProcedureNot(ProcedureUnaryOperator):
    name = 'not@py'
    native_function = staticmethod(lambda x: not x)


class ProcedureNegate(ProcedureUnaryOperator):
    name = 'neg@py'
    native_function = staticmethod(lambda x: -x)


class ProcedureSquare(ProcedureUnaryOperator):
    name = 'sq@py'
    native_function = staticmethod(lambda x: x * x)


class ProcedureAnd(ProcedureBinaryOperator):
    name = 'and@py'
    native_function = staticmethod(lambda x, y: x and y)


class ProcedureOr(ProcedureBinaryOperator):
    name = 'or@py'
    native_function = staticmethod(lambda x, y: x or y)


class ProcedureAdd(ProcedureBinaryOperator):
    name = 'add@py'
    native_function = staticmethod(lambda x, y: x + y)


class ProcedureSubtract(ProcedureBinaryOperator):
    name = 'sub@py'
    native_function = staticmethod(lambda x, y: x - y)


class ProcedureMultiply(ProcedureBinaryOperator):
    name = 'mul@py'
    native_function = staticmethod(lambda x, y: x * y)


class ProcedureDivide(ProcedureBinaryOperator):
    name = 'div@py'
    native_function = staticmethod(lambda x, y: x / y)


class ProcedureModulo(ProcedureBinaryOperator):
    name = 'mod@py'
    native_function = staticmethod(lambda x, y: x % y)


class ProcedureModDivide(ProcedureBinaryOperator):
    name = 'mod_div@py'
    native_function = staticmethod(lambda x, y: x // y)


class ProcedurePower(ProcedureBinaryOperator):
    name = 'pow@py'
    native_function = staticmethod(lambda x, y: x ** y)


class ProcedureEqual(ProcedureComparator):
    name = 'eq@py'
    native_function = staticmethod(lambda x, y: x == y)


class ProcedureNotEqual(ProcedureComparator):
    name = 'ne@py'
    native_function = staticmethod(lambda x, y: x != y)


class ProcedureLessThan(ProcedureComparator):
    name = 'lt@py'
    native_function = staticmethod(lambda x, y: x < y)


class ProcedureLessThanOrEqual(ProcedureComparator):
    name = 'lte@py'
    native_function = staticmethod(lambda x, y: x <= y)


class ProcedureGreaterThan(ProcedureComparator):
    name = 'gt@py'
    native_function = staticmethod(lambda x, y: x > y)


class ProcedureGreaterThanEqual(ProcedureComparator):
    name = 'gte@py'
    native_function = staticmethod(lambda x, y: x >= y)


class ProcedureFactoryBasic(IProcedureFactory):

    def __init__(self, service_site, **kwargs):
        self.procedure_classes = {p.name: p for p in [
            ProcedureComposite,
            ProcedureNot,
            ProcedureNegate,
            ProcedureSquare,
            ProcedureAnd,
            ProcedureOr,
            ProcedureAdd,
            ProcedureSubtract,
            ProcedureMultiply,
            ProcedureDivide,
            ProcedureModulo,
            ProcedureModDivide,
            ProcedurePower,
            ProcedureEqual,
            ProcedureNotEqual,
            ProcedureLessThan,
            ProcedureLessThanOrEqual,
            ProcedureGreaterThan,
            ProcedureGreaterThanEqual,
            ProcedureSwitch,
            ProcedureGate,
            ProcedureFunnel,
        ]}

    def create(self, class_name, **kwargs):
        procedure_class = self.procedure_classes.get(class_name)
        return procedure_class and procedure_class(**kwargs)

    def register_class(self, class_name, procedure_class, **kwargs):
        assert class_name not in self.procedure_classes
        self.procedure_classes[class_name] = procedure_class

    def iterate_classes(self):
        return self.procedure_classes.keys()
