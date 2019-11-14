from base64 import urlsafe_b64encode
from uuid import uuid1

from mbcom.interfaces import (
    IProcedureJoint,
    IProcedureJointFactory,
)


def joint_validate(joints, indices, procedure, signatures):
    signatures_in = procedure.get_input_signatures()

    if len(joints) != len(indices):
        raise AssertionError('input number miss match')

    for i, joint, sig in zip(
            indices,
            joints,
            signatures,
    ):
        if not isinstance(i, int):
            raise AssertionError('incorrect input type')

        if not joint:
            input_sig = signatures_in
        elif isinstance(joint, ProcedureJointBasic):
            if joint.outer_procedure != procedure:
                raise AssertionError('incorrect outer procedure')
            input_sig = joint.inner_procedure.get_output_signatures()
        else:
            raise AssertionError('incorrect flow type')

        if sig != input_sig[i]:
            raise AssertionError('input type miss match')


def joint_run(joint, procedure_data_list, **kwargs):
    assert isinstance(joint, ProcedureJointBasic)
    input_data_list = [
        joint_run(joint, procedure_data_list, **kwargs)[i] if
        joint else procedure_data_list[i]
        for joint, i in joint.get_joints()
    ]
    return joint.inner_procedure.run(input_data_list, **kwargs)


class ProcedureJointBasic(IProcedureJoint):
    has_breakpoint = False

    def __init__(
            self,
            signature=None,
            inner_procedure=None,
            outer_procedure=None,
    ):
        assert inner_procedure is not outer_procedure
        # outer procedure should be a composite procedure
        outer_procedure.get_joints()
        self.signature = signature or urlsafe_b64encode(
            uuid1().bytes).strip(b'=').decode('utf8')
        self.inner_procedure = inner_procedure
        self.outer_procedure = outer_procedure
        self.input_indices = []
        self.input_flows = []

    def get_signature(self):
        return self.signature

    def get_inner_procedure(self):
        return self.inner_procedure

    def get_outer_procedure(self):
        return self.outer_procedure

    def get_breakpoint(self):
        return self.has_breakpoint

    def set_breakpoint(self, is_breakpoint):
        self.has_breakpoint = is_breakpoint

    def get_joints(self):
        return [(f, i) for f, i in zip(
            self.input_flows, self.input_indices)]

    def set_joints(
            self,
            input_joints,
            input_indices,
    ):
        joint_validate(
            input_joints,
            input_indices,
            self.outer_procedure,
            self.inner_procedure.get_input_signatures(),
        )
        self.input_flows = input_joints
        self.input_indices = input_indices


class ProcedureJointFactory(IProcedureJointFactory):

    def __init__(self, service_site, **kwargs):
        pass

    def create(self, inner_procedure, outer_procedure, **kwargs):
        return ProcedureJointBasic(
            inner_procedure=inner_procedure,
            outer_procedure=outer_procedure,
            **kwargs
        )
