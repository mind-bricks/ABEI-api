from django_filters.rest_framework import (
    filters,
    filterset,
)

from .models import (
    ProcedureRun,
)


class ProcedureRunFilterSet(filterset.FilterSet):
    created_time = filters.IsoDateTimeFromToRangeFilter()
    finished_time = filters.IsoDateTimeFromToRangeFilter()

    class Meta:
        model = ProcedureRun
        fields = [
            'status',
            'created_time',
            'finished_time',
        ]


class ProcedureRunLogFilterSet(ProcedureRunFilterSet):
    site = filters.CharFilter(
        field_name='procedure__site__signature',
    )
    procedure = filters.CharFilter(
        field_name='procedure__signature',
    )

    class Meta(ProcedureRunFilterSet.Meta):
        fields = [
            'site',
            'procedure',
            *ProcedureRunFilterSet.Meta.fields,
        ]
