import os
import random

from abei.interfaces import (
    IProcedureBuilder,
    IProcedure,
    IProcedureFactory,
    IProcedureDataFactory,
    IProcedureJoint,
    IProcedureJointFactory,
    IProcedureSite,
    IProcedureSiteFactory,
    service_entry as _
)
from abei.implements.procedure import (
    ProcedureBasic,
    ProcedureDataBasic,
)

from .basic import TestCaseBasic


class TestProcedure(TestCaseBasic):
    service_config_files = [
        'test-components-basic.yml',
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

    def test_procedure_builder(self):
        builder = self.service_site.get_service(_(IProcedureBuilder))
        site_factory = self.service_site.get_service(_(IProcedureSiteFactory))
        data_factory = self.service_site.get_service(_(IProcedureDataFactory))
        site = site_factory.create(None)
        builder.load_yaml(site, os.path.join(
            self.service_config_dir,
            'test-procedures-1.yml'
        ))
        procedure = site.get_procedure('test-procedure-1.1')
        self.assertIsNotNone(procedure)
        self.assertEqual(
            procedure.get_docstring(),
            'this is test procedure 1.1'
        )
        input_1 = data_factory.create('int@py')
        input_2 = data_factory.create('int@py')
        input_1.set_value(1)
        input_2.set_value(2)
        outputs = procedure.run([input_1, input_2])
        self.assertEqual(len(outputs), 2)
        self.assertTrue(all(outputs))
        self.assertEqual(outputs[0].get_value(), 3)
        self.assertEqual(outputs[1].get_value(), -1)

        procedure = site.get_procedure('test-procedure-1.2')
        self.assertIsNotNone(procedure)
        self.assertEqual(
            procedure.get_docstring(),
            'this is test procedure 1.2'
        )
        input_1 = data_factory.create('int@py')
        input_2 = data_factory.create('int@py')
        input_1.set_value(1)
        input_2.set_value(2)
        self.assertRaises(
            AssertionError,
            lambda: procedure.run([input_1, input_2])
        )

        input_1 = data_factory.create('float@py')
        input_2 = data_factory.create('float@py')
        input_1.set_value(2.0)
        input_2.set_value(3.0)
        outputs = procedure.run([input_1, input_2])
        self.assertEqual(len(outputs), 2)
        self.assertTrue(all(outputs))
        self.assertEqual(outputs[0].get_value(), 30)
        self.assertEqual(outputs[1].get_value(), 11)

        procedure = site.get_procedure('test-procedure-1.3')
        self.assertIsNotNone(procedure)
        self.assertEqual(procedure.get_docstring(), '(x + y) * z')
        x = random.random() * random.randint(1, 10)
        y = random.random() * random.randint(1, 10)
        z = random.random() * random.randint(1, 10)
        input_1 = data_factory.create('float@py', value=x)
        input_2 = data_factory.create('float@py', value=y)
        input_3 = data_factory.create('float@py', value=z)
        outputs = procedure.run([input_1, input_2, input_3])
        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0].get_value(), (x + y) * z)

        procedure = site.get_procedure('test-procedure-1.4')
        self.assertIsNotNone(procedure)
        self.assertEqual(procedure.get_docstring(), 'x + y * z')
        x = random.random() * random.randint(1, 10)
        y = random.random() * random.randint(1, 10)
        z = random.random() * random.randint(1, 10)
        input_1 = data_factory.create('float@py', value=x)
        input_2 = data_factory.create('float@py', value=y)
        input_3 = data_factory.create('float@py', value=z)
        outputs = procedure.run([input_1, input_2, input_3])
        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0].get_value(), x + y * z)
