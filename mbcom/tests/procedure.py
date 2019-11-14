import os

from mbcom.interfaces import (
    # IProcedureBuilder,
    IProcedure,
    IProcedureFactory,
    IProcedureDataFactory,
    IProcedureJoint,
    IProcedureJointFactory,
    IProcedureSite,
    IProcedureSiteFactory,
    service_entry as _
)
from mbcom.implements.procedure import (
    ProcedureBasic,
    ProcedureDataBasic,
)

from .basic import TestCaseBasic


class TestProcedure(TestCaseBasic):
    service_config_files = [
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            'fixtures',
            'test-components-basic.yml'
        ),
    ]

    def test_procedure_factory(self):
        service = self.service_site.get_service(_(IProcedureFactory))
        procedure_classes = list(service.iterate_classes())
        procedure_class_count = len(procedure_classes)
        self.assertNotEqual(procedure_class_count, 0)

        service.register_class(ProcedureBasic.signature, ProcedureBasic)
        procedure_classes = list(service.iterate_classes())
        self.assertEqual(len(procedure_classes), procedure_class_count + 1)

        instance = service.create(ProcedureBasic.signature)
        self.assertIsInstance(instance, ProcedureBasic)

    def test_procedure_data_factory(self):
        service = self.service_site.get_service(_(IProcedureDataFactory))
        data_classes = list(service.iterate_classes())
        data_class_count = len(data_classes)
        self.assertNotEqual(data_class_count, 0)

        service.register_class(
            ProcedureDataBasic.signature, ProcedureDataBasic)
        data_classes = list(service.iterate_classes())
        self.assertEqual(len(data_classes), data_class_count + 1)

        instance = service.create(ProcedureDataBasic.signature)
        self.assertIsInstance(instance, ProcedureDataBasic)

    def test_procedure_joint_factory(self):
        factory = self.service_site.get_service(_(IProcedureFactory))
        outer_procedure = factory.create('composite@py')
        inner_procedure = factory.create('add@py', data_signature='int@py')
        self.assertIsInstance(outer_procedure, IProcedure)
        self.assertIsInstance(inner_procedure, IProcedure)
        joint_factory = \
            self.service_site.get_service(_(IProcedureJointFactory))
        self.assertRaises(
            AssertionError,
            lambda: joint_factory.create(inner_procedure, inner_procedure))
        self.assertRaises(
            AssertionError,
            lambda: joint_factory.create(outer_procedure, outer_procedure))
        self.assertRaises(
            AssertionError,
            lambda: joint_factory.create(outer_procedure, inner_procedure))
        procedure_joint = \
            joint_factory.create(inner_procedure, outer_procedure)
        self.assertIsInstance(procedure_joint, IProcedureJoint)

    def test_procedure_site_factory(self):
        service = self.service_site.get_service(_(IProcedureSiteFactory))
        instance = service.create(None)
        procedures = instance.iterate_procedures()
        procedure_1 = instance.query_procedure('int@py:add@py')
        procedure_2 = instance.query_procedure('int@py:add@py', depth=0)
        self.assertEqual(len(procedures), 0)
        self.assertIsNotNone(procedure_1)
        self.assertIsNone(procedure_2)

        base_sites = instance.get_base_sites()
        self.assertIsInstance(instance, IProcedureSite)
        self.assertEqual(len(base_sites), 1)

        instance = base_sites[0]
        procedures = instance.iterate_procedures()
        procedure_3 = instance.query_procedure('int@py:add@py', depth=0)
        self.assertNotEqual(len(procedures), 0)
        self.assertIs(procedure_1, procedure_3)
