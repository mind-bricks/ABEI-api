from django_filters.rest_framework import (
    filterset,
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
    class Meta:
        model = Procedure
        fields = [
            'signature',
        ]
