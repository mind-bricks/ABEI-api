from base64 import urlsafe_b64encode
from uuid import uuid1

from mbcom.interfaces import (
    IProcedure,
    IProcedureData,
    IProcedureFactory,
)

from .data_basic import (
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

    def get_joints(self):
        raise AssertionError('not supported')

    def set_joints(self, output_joints, output_indices):
        raise AssertionError('not supported')

    def get_docstring(self):
        return self.docstring

    def set_docstring(self, docstring):
        self.docstring = docstring

    def run(self, procedure_data_list, **kwargs):
        self.run_check(procedure_data_list, self.input_signatures)
        return self.run_directly(procedure_data_list, **kwargs)

    @staticmethod
    def run_check(procedure_data_list, signatures):
        if len(procedure_data_list) != len(signatures):
            raise AssertionError('invalid data list')

        for d, sig in zip(procedure_data_list, signatures):
            if d is None:
                continue
            if not isinstance(d, IProcedureData):
                raise AssertionError('invalid data list')
            if not d.get_signature() != sig:
                raise AssertionError('data signature miss match')

    def run_directly(self, procedure_data_list, **kwargs):
        return [None] * len(self.output_signatures)


class ProcedureComposite(ProcedureBasic):
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

    def set_joints(self, output_joints, output_indices):
        joint_validate(
            output_joints,
            output_indices,
            self,
            self.output_signatures,
        )
        self.output_joints = output_joints
        self.output_indices = output_indices

    def run_directly(self, procedure_data_list, **kwargs):
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
    native_function = (lambda x: x)

    def __init__(self, data_signature=''):
        super().__init__(data_signature)
        self.input_signatures = [data_signature]
        self.output_signatures = [data_signature]

    def run_directly(self, procedure_data_list, **kwargs):
        ret = procedure_data_list[0].clone()
        ret.set_value(self.native_function(
            procedure_data_list[0].get_value()))
        return [ret]


class ProcedureBinaryOperator(ProcedureBuiltin):
    name = 'binary_op@py'
    native_function = (lambda x, y: x)

    def __init__(self, data_signature=''):
        super().__init__(data_signature)
        self.input_signatures = [data_signature, data_signature]
        self.output_signatures = [data_signature]

    def run_directly(self, procedure_data_list, **kwargs):
        ret = procedure_data_list[0].clone()
        ret.set_value(self.native_function(
            procedure_data_list[0].get_value(),
            procedure_data_list[1].get_value(),
        ))
        return [ret]


class ProcedureComparator(ProcedureBuiltin):
    name = 'compare@py'
    native_function = (lambda x, y: True)

    def __init__(self, data_signature=''):
        super().__init__(data_signature)
        self.input_signatures = [data_signature, data_signature]
        self.output_signatures = [data_signature]

    def run_directly(self, procedure_data_list, **kwargs):
        ret = ProcedureDataBool()
        ret.set_value(self.native_function(
            procedure_data_list[0].get_value(),
            procedure_data_list[1].get_value(),
        ))
        return [ret]


class ProcedureBranch(ProcedureBuiltin):
    name = 'branch@py'

    def __init__(self, data_signature=''):
        super().__init__(data_signature)
        self.data_signature = data_signature
        self.input_signatures = ['bool@py', data_signature]
        self.output_signatures = [data_signature, data_signature]

    def run_directly(self, procedure_data_list, **kwargs):
        switch = procedure_data_list[0].get_value()
        ret = procedure_data_list[1].clone()
        return switch and [None, ret] or [ret, None]


class ProcedureRouter2(ProcedureBuiltin):
    name = 'router2@py'

    def __init__(self, data_signature=''):
        super().__init__(data_signature)
        self.input_signatures = [
            'int@py',
            data_signature,
        ]
        self.output_signatures = [
            data_signature,
            data_signature,
        ]

    def run_directly(self, procedure_data_list, **kwargs):
        gate = procedure_data_list[0].get_value()
        ret = procedure_data_list[1]
        return [
            gate & 1 and ret.clone() or None,
            gate & 2 and ret.clone() or None,
        ]


class ProcedureRouter4(ProcedureBuiltin):
    name = 'router4@py'

    def __init__(self, data_signature=''):
        super().__init__(data_signature)
        self.input_signatures = [
            'int@py',
            data_signature,
        ]
        self.output_signatures = [
            data_signature,
            data_signature,
            data_signature,
            data_signature,
        ]

    def run_directly(self, procedure_data_list, **kwargs):
        gate = procedure_data_list[0].get_value()
        ret = procedure_data_list[1]
        return [
            gate & 1 and ret.clone() or None,
            gate & 2 and ret.clone() or None,
            gate & 4 and ret.clone() or None,
            gate & 8 and ret.clone() or None,
        ]


class ProcedureNot(ProcedureUnaryOperator):
    name = 'not@py'
    native_function = (lambda x: not x)


class ProcedureNegate(ProcedureUnaryOperator):
    name = 'neg@py'
    native_function = (lambda x: -x)


class ProcedureSquare(ProcedureUnaryOperator):
    name = 'sq@py'
    native_function = (lambda x: x * x)


class ProcedureAnd(ProcedureBinaryOperator):
    name = 'and@py'
    native_function = (lambda x, y: x and y)


class ProcedureOr(ProcedureBinaryOperator):
    name = 'or@py'
    native_function = (lambda x, y: x or y)


class ProcedureAdd(ProcedureBinaryOperator):
    name = 'add@py'
    native_function = (lambda x, y: x + y)


class ProcedureSubtract(ProcedureBinaryOperator):
    name = 'sub@py'
    native_function = (lambda x, y: x - y)


class ProcedureMultiply(ProcedureBinaryOperator):
    name = 'mul@py'
    native_function = (lambda x, y: x * y)


class ProcedureDivide(ProcedureBinaryOperator):
    name = 'div@py'
    native_function = (lambda x, y: x / y)


class ProcedureModulo(ProcedureBinaryOperator):
    name = 'mod@py'
    native_function = (lambda x, y: x % y)


class ProcedureModDivide(ProcedureBinaryOperator):
    name = 'mod_div@py'
    native_function = (lambda x, y: x // y)


class ProcedurePower(ProcedureBinaryOperator):
    name = 'pow@py'
    native_function = (lambda x, y: x ** y)


class ProcedureEqual(ProcedureComparator):
    name = 'eq@py'
    native_function = (lambda x, y: x == y)


class ProcedureNotEqual(ProcedureComparator):
    name = 'ne@py'
    native_function = (lambda x, y: x != y)


class ProcedureLessThan(ProcedureComparator):
    name = 'lt@py'
    native_function = (lambda x, y: x < y)


class ProcedureLessThanOrEqual(ProcedureComparator):
    name = 'lte@py'
    native_function = (lambda x, y: x <= y)


class ProcedureGreaterThan(ProcedureComparator):
    name = 'gt@py'
    native_function = (lambda x, y: x > y)


class ProcedureGreaterThanEqual(ProcedureComparator):
    name = 'gte@py'
    native_function = (lambda x, y: x >= y)


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
            ProcedureBranch,
            ProcedureRouter2,
            ProcedureRouter4,
        ]}

    def create(self, signature, **kwargs):
        procedure_class = self.procedure_classes.get(signature)
        return procedure_class and procedure_class(**kwargs)

    def register_class(self, signature, procedure_class, **kwargs):
        assert signature not in self.procedure_classes
        self.procedure_classes[signature] = procedure_class

    def iterate_classes(self):
        return self.procedure_classes.keys()
