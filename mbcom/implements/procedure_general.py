from mbcom.interfaces.procedure import (
    IProcedure,
    IProcedureData,
    IProcedureFlow,
    IProcedureSite,
    IProcedureConfiguration,
    ProcedureException,
)
from .service_basic import ServiceBasic
from .utils import FileLikeWrapper


def validate_joints(
        joint_flows,
        joint_indices,
        outer_procedure,
        signatures,
):
    assert isinstance(outer_procedure, IProcedure)
    signatures_in = outer_procedure.get_input_signatures()

    if len(joint_flows) != len(joint_indices):
        raise ProcedureException('input number miss match')

    for i, flow, sig in zip(
            joint_indices,
            joint_flows,
            signatures,
    ):
        if not isinstance(i, int):
            raise ProcedureException('incorrect input type')

        if not flow:
            input_sig = signatures_in
        elif isinstance(flow, IProcedureFlow):
            if flow.get_outer_procedure() != outer_procedure:
                raise ProcedureException('incorrect outer procedure')
            input_sig = flow.get_inner_procedure().get_output_signatures()
        else:
            raise ProcedureException('incorrect flow type')

        if sig != input_sig[i]:
            raise ProcedureException('input type miss match')


def validate_data(
        data_list,
        signatures,
):
    if len(data_list) != len(signatures):
        raise ProcedureException('invalid data list')

    for data, sig in zip(data_list, signatures):
        if data is None:
            continue
        if not isinstance(data, IProcedureData):
            raise ProcedureException('invalid data list')
        if not data.get_signature() != sig:
            raise ProcedureException('data signature miss match')


def run_flow(flow, procedure_data_list, **kwargs):
    input_data_list = [
        run_flow(f, procedure_data_list, **kwargs)[i] if
        f else
        procedure_data_list[i]
        for f, i in flow.get_joints()
    ]
    inner_procedure = flow.get_inner_procedure()
    return inner_procedure.run(input_data_list, **kwargs)


class ProcedureFlow(IProcedureFlow):
    has_breakpoint = False

    def __init__(
            self,
            signature,
            inner_procedure,
            outer_procedure,
    ):
        self.inner_procedure = inner_procedure
        self.outer_procedure = outer_procedure
        self.signature = signature
        self.input_indices = []
        self.input_flows = []

    def get_signature(self):
        return self.signature

    def get_joints(self):
        return [(f, i) for f, i in zip(
            self.input_flows, self.input_indices)]

    def set_joints(
            self,
            input_flows,
            input_indices,
    ):
        validate_joints(
            input_flows,
            input_indices,
            self.outer_procedure,
            self.inner_procedure.get_input_signatures(),
        )
        self.input_flows = input_flows
        self.input_indices = input_indices

    def get_inner_procedure(self):
        return self.inner_procedure

    def get_outer_procedure(self):
        return self.outer_procedure

    def get_breakpoint(self):
        return self.has_breakpoint

    def set_breakpoint(self, is_breakpoint):
        self.has_breakpoint = is_breakpoint


class Procedure(IProcedure):
    def __init__(
            self,
            signature,
            docstring='',
            input_signatures=None,
            output_signatures=None,
    ):
        self.signature = signature
        self.docstring = docstring
        self.input_signatures = input_signatures or []
        self.output_signatures = output_signatures or []
        self.output_indices = []
        self.output_flows = []

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

    def get_joints(self):
        return [(f, i) for f, i in zip(
            self.output_flows, self.output_indices)]

    def set_joints(self, output_flows, output_indices):
        validate_joints(
            output_flows,
            output_indices,
            self,
            self.output_signatures,
        )
        self.output_flows = output_flows
        self.output_indices = output_indices

    def run(self, procedure_data_list, **kwargs):
        # validate input data
        validate_data(procedure_data_list, self.input_signatures)
        output_data_list = [
            run_flow(f, procedure_data_list, **kwargs)[i] if
            f else
            procedure_data_list[i]
            for f, i in self.get_joints()
        ]
        # validate output data
        validate_data(output_data_list, self.output_signatures)
        return output_data_list


class ProcedureSite(IProcedureSite):

    def __init__(self):
        self.procedure_mapping = {}

    def get_procedure(self, signature):
        procedure = self.query_procedure(signature)
        if not procedure:
            raise LookupError('procedure not found')
        return procedure

    def query_procedure(self, signature):
        return self.procedure_mapping.get(str(signature))

    def register_procedure(self, procedure):
        assert isinstance(procedure, IProcedure)
        name = str(procedure.get_signature())
        if name in self.procedure_mapping:
            raise ProcedureException('procedure already registered')

        self.procedure_mapping[name] = procedure
        return procedure


class ProcedureConfiguration(ServiceBasic, IProcedureConfiguration):
    @classmethod
    def get_dependencies(cls):
        return ['PyYAML']

    @staticmethod
    def load_object(procedure_site, config_object):
        pass

    def load_json(self, procedure_site, file_or_filename):
        import json

        with FileLikeWrapper(file_or_filename) as file:
            self.load_object(procedure_site, json.loads(file.read()))

    def save_json(self, procedure_site, file_or_filename):
        raise NotImplementedError

    def load_yaml(self, procedure_site, file_or_filename):
        import yaml

        with FileLikeWrapper(file_or_filename) as file:
            self.load_object(procedure_site, yaml.safe_load(file))

    def save_yaml(self, procedure_site, file_or_filename):
        raise NotImplementedError
