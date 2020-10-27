from django.utils.functional import LazyObject

from abei.interfaces import (
    IProcedure,
    IProcedureDetail,
    IProcedureFactory,
    IProcedureDataFactory,
    IProcedureJointFactory,
    IProcedureSiteFactory,
    service_entry as _,
)

from ..settings import default_service_site


class ProcedureBuilder(object):
    def __init__(self):
        self.factory = default_service_site.get_service(
            _(IProcedureFactory)
        )
        self.joint_factory = default_service_site.get_service(
            _(IProcedureJointFactory)
        )
        self.site_factory = default_service_site.get_service(
            _(IProcedureSiteFactory)
        )
        self.site_cache = {}
        self.site_default = self.site_factory.create(
            None, builtin=True)

    def load_model_site(self, site, clear=False):
        if clear:
            self.site_cache.clear()

        site_object = (
            self.site_cache.get(site.signature)
            if site else self.site_default
        )
        if site_object:
            return site_object

        site_builtin = bool(site.signature == 'builtin')
        site_bases = [
            self.load_model_site(site)
            for site in site.base_sites.all()
        ]
        assert not (site_builtin and site_bases)

        site_object = self.site_factory.create(
            site_bases,
            builtin=site_builtin,
        )
        self.site_cache[site.signature] = site_object
        return site_object

    def load_model_joint(self, joint, procedure_object):
        joint_object = self.joint_factory.create(
            self.load_model(joint.inner_procedure),
            procedure_object,
            signature=joint.signature,
        )
        # inputs ----------------------
        inputs = list(joint.links.order_by('index').all())
        input_joints = [
            i.input_joint and
            self.load_model_joint(
                i.input_joint,
                procedure_object,
            ) for i in inputs
        ]
        input_indices = [
            i.input_index for i in inputs
        ]
        joint_object.set_joints(
            input_joints,
            input_indices,
        )
        return joint_object

    def load_model(self, procedure, clear=False):
        site_object = self.load_model_site(
            procedure.site,
            clear=clear,
        )
        procedure_object = site_object.query_procedure(
            procedure.signature,
            depth=0,
        )
        if procedure_object:
            return procedure_object

        # inputs -----------------------
        inputs = list(
            procedure.inputs.order_by('index').all()
        )

        # outputs ----------------------
        outputs = list(
            procedure.outputs.select_related(
                'output_link').order_by('index').all()
        )

        procedure_object = self.factory.create(
            'composite',
            signature=procedure.signature,
            docstring=procedure.docstring,
            input_signatures=[i.signature for i in inputs],
            output_signatures=[o.signature for o in outputs],
        )

        assert (
            isinstance(procedure_object, IProcedure) and
            isinstance(procedure_object, IProcedureDetail)
        )

        # joints ----------------------
        output_joints = [
            o.output_link.output_joint and
            self.load_model_joint(
                o.output_link.output_joint,
                procedure_object,
            ) for o in outputs
        ]

        output_indices = [
            o.output_link.output_index for o in outputs
        ]

        procedure_object.set_joints(
            output_joints,
            output_indices,
        )

        # register to site ----------------
        site_object.register_procedure(procedure_object)
        return procedure_object


class DefaultProcedureBuilder(LazyObject):

    def _setup(self):
        self._wrapped = ProcedureBuilder()


class DefaultProcedureDataBuilder(LazyObject):

    def _setup(self):
        self._wrapped = default_service_site.get_service(
            _(IProcedureDataFactory)
        )


default_procedure_builder = DefaultProcedureBuilder()
default_procedure_data_builder = DefaultProcedureDataBuilder()
