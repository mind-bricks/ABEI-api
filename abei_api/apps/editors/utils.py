from abei.interfaces import (
    IProcedureSiteFactory,
    service_entry as _,
)

from ..settings import (
    default_service_site,
)
from .models import (
    Procedure,
    ProcedureInput,
    ProcedureOutput,
    ProcedureSite,
)


def init_sites():
    site_factory = default_service_site.get_service(
        _(IProcedureSiteFactory)
    )
    site = site_factory.create(None, builtin=True)
    site_instance, __ = ProcedureSite.objects.get_or_create(
        signature='builtin')

    for procedure_signature in site.iterate_procedures():
        procedure = site.query_procedure(procedure_signature)
        procedure_instance, __ = Procedure.objects.get_or_create(
            signature=procedure_signature,
            site=site_instance,
            defaults={'docstring': procedure.get_docstring()},
        )

        for i, input_signature in enumerate(
                procedure.get_input_signatures()
        ):
            ProcedureInput.objects.get_or_create(
                procedure=procedure_instance,
                signature=input_signature,
                index=i,
            )

        for i, output_signature in enumerate(
                procedure.get_output_signatures()
        ):
            ProcedureOutput.objects.get_or_create(
                procedure=procedure_instance,
                signature=output_signature,
                index=i,
            )
