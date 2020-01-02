from django_filters.rest_framework import (
    filterset,
    CharFilter,
)

from .models import (
    ProcedureSite,
    Procedure,
)


class ProcedureSiteFilterSet(filterset.FilterSet):
    class Meta:
        model = ProcedureSite
        fields = [
            'signature',
        ]


class ProcedureFilterSet(filterset.FilterSet):
    site = CharFilter(
        field_name='site__signature',
    )

    class Meta:
        model = Procedure
        fields = [
            'signature',
            'site',
        ]
