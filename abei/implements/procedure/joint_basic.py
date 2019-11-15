from base64 import urlsafe_b64encode
from uuid import uuid1

from abei.interfaces import (
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
    input_joints = joint.get_joints()

    procedure_cache = (
        kwargs.setdefault('procedure_cache', {}) if
        joint.use_cache else None
    )
    # try to get output from cache
    if isinstance(procedure_cache, dict):
        output_data_list = procedure_cache.get(joint.signature)
        if isinstance(output_data_list, (list, tuple)):
            return output_data_list

    input_data_list = [
        joint_run(joint, procedure_data_list, **kwargs)[i] if
        joint else procedure_data_list[i]
        for joint, i in input_joints
    ]

    output_data_list = joint.inner_procedure.run(
        input_data_list, **kwargs)

    # try to save output to cache
    if isinstance(procedure_cache, dict):
        procedure_cache[joint.signature] = output_data_list

    return output_data_list


class ProcedureJointBasic(IProcedureJoint):
    use_breakpoint = False
    use_cache = False

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

    def has_breakpoint(self):
        return self.use_breakpoint

    def has_cache(self):
        return self.use_cache

    def set_has_breakpoint(self, has_breakpoint):
        self.use_breakpoint = has_breakpoint

    def set_has_cache(self, has_cache):
        self.use_cache = has_cache

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
