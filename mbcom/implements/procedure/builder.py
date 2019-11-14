from mbcom.interfaces import (
    IProcedureFactory,
    IProcedureJointFactory,
    IProcedureBuilder,
    service_entry as _
)

from ..service_basic import ServiceBasic
from ..util import (
    FileLikeWrapper,
    LazyProperty,
)


class ProcedureBuilder(ServiceBasic, IProcedureBuilder):

    def __init__(self, service_site, **kwargs):
        self.service_site = service_site

    @LazyProperty
    def procedure_factory(self):
        return self.service_site.get_service(_(IProcedureFactory))

    @LazyProperty
    def procedure_joint_factory(self):
        return self.service_site.get_service(_(IProcedureJointFactory))

    @classmethod
    def get_dependencies(cls):
        return ['PyYAML']

    def load_procedure(self, procedure_site, procedure_object):
        if not isinstance(procedure_object, dict):
            raise ValueError(
                'invalid procedure in configuration file')

        input_signatures = procedure_object.get('input_signatures', [])
        if not isinstance(input_signatures, list):
            raise ValueError(
                'invalid procedure input signatures')

        input_signatures = [str(sig) for sig in input_signatures]

        output_signatures = procedure_object.get('output_signatures', [])
        if not isinstance(output_signatures, list):
            raise ValueError(
                'invalid procedure output signatures')

        output_signatures = [str(sig) for sig in output_signatures]

        procedure = self.procedure_factory.create(
            'composite@py',
            signature=str(procedure_object.get('signature', '')),
            docstring=str(procedure_object.get('docstring', '')),
            input_signatures=input_signatures,
            output_signatures=output_signatures,
        )

        procedure_joints = procedure_object.get('joints', {})
        self.load_joints(
            procedure_site,
            procedure,
            procedure_joints,
        )

        procedure_output_joints = procedure_object.get('output_joints', [])
        if not isinstance(procedure_output_joints, list):
            raise ValueError('invalid procedure joints')

        input_joints = []
        input_indices = []
        for joint_key, i in procedure_output_joints:
            if joint_key is None:
                input_joints.append(None)
            elif joint_key in procedure_joints:
                input_joints.append(
                    procedure_joints[joint_key]['instance'])
            else:
                raise ValueError('invalid procedure joint')
            input_indices.append(i)

        procedure.set_joints(input_joints, input_indices)
        procedure_site.register_procedure(procedure)

    def load_joints(self, procedure_site, procedure, joint_objects):
        if not isinstance(joint_objects, dict):
            raise ValueError('invalid procedure joints')

        # create joints
        for joint_signature, joint_object in joint_objects.items():
            if not isinstance(joint_object, dict):
                raise ValueError('invalid procedure joint config')
            joint_procedure = procedure_site.get_procedure(
                joint_object.get('procedure'))
            joint = self.procedure_joint_factory.create(
                joint_procedure,
                procedure,
                signature=joint_signature,
            )
            joint_object['instance'] = joint

        # connect joints
        for joint_signature, joint_object in joint_objects.items():
            input_joint_objects = joint_object.get('input_joints', [])
            if not isinstance(input_joint_objects, list):
                raise ValueError('invalid procedure joint config')

            joint = joint_object['instance']
            input_joints = []
            input_indices = []
            for joint_key, i in input_joint_objects:
                if joint_key is None:
                    input_joints.append(None)
                elif joint_key in joint_objects:
                    input_joints.append(
                        joint_objects[joint_key]['instance'])
                else:
                    raise ValueError('invalid joint')
                input_indices.append(i)
            joint.set_joints(input_joints, input_indices)

    def load_object(self, procedure_site, config_object):
        if not isinstance(config_object, (tuple, list)):
            raise ValueError('invalid procedure configuration file')

        for config_item in config_object:
            self.load_procedure(procedure_site, config_item)

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
