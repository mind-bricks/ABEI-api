from django_filters.rest_framework import (
    filters,
    filterset,
)

from .models import (
    ProcedureRun,
)


class ProcedureRunFilterSet(filterset.FilterSet):
    site = filters.CharFilter(
        field_name='procedure__site__signature',
    )
    procedure = filters.CharFilter(
        field_name='procedure__signature',
    )
    created_time = filters.IsoDateTimeFromToRangeFilter()
    finished_time = filters.IsoDateTimeFromToRangeFilter()

    class Meta:
        model = ProcedureRun
        fields = [
            'site',
            'procedure',
            'status',
            'created_time',
            'finished_time',
        ]
