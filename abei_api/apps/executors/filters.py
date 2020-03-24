from django_filters.rest_framework import (
    filters,
    filterset,
)

from .models import (
    ProcedureRun,
)


class ProcedureRunFilterSet(filterset.FilterSet):
    procedure = filters.UUIDFilter(
        field_name='procedure__uuid',
    )
    created_time = filters.IsoDateTimeFromToRangeFilter()
    finished_time = filters.IsoDateTimeFromToRangeFilter()

    class Meta:
        model = ProcedureRun
        fields = [
            'procedure',
            'status',
            'created_time',
            'finished_time',
        ]
