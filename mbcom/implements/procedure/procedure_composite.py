from base64 import urlsafe_b64encode
from uuid import uuid1

from mbcom.interfaces import (
    service_entry as _
)
from .procedure_basic import (
    IProcedureFactory,
    ProcedureBasic,
)
from .joint_basic import (
    joint_validate,
    joint_run,
)


class ProcedureComposite(ProcedureBasic):
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


class ProcedureFactoryComposite(IProcedureFactory):

    def __init__(self, service_site, **kwargs):
        self.factory = service_site.query_service(
            _(IProcedureFactory, kwargs.get('inner', '')))

    def create(self, template_name, *args, **kwargs):
        if template_name == 'composite':
            return ProcedureComposite(*args, **kwargs)

        return self.factory and self.factory.create(
            template_name, *args, **kwargs)
