from django.apps import apps
from rest_framework import (
    exceptions,
    decorators,
    mixins,
    response,
    status,
    viewsets,
)

from ..mixins import NestedViewSetMixin
from ..permissions import UserPermission

from .filters import (
    ProcedureRunFilterSet,
    ProcedureRunLogFilterSet,
)
from .models import (
    ProcedureRun,
)
from .serializers import (
    ProcedureRunSerializer,
    ProcedureRunLogSerializer,
    ProcedureRunCreateSyncSerializer,
    ProcedureRunCreateASyncSerializer,
)


class ProcedureSiteViewSet(viewsets.GenericViewSet):
    """
    viewset that do nothing
    """


class ProcedureViewSet(viewsets.GenericViewSet):
    """
    viewset that do nothing
    """


class ProcedureRunViewSet(
    NestedViewSetMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    filter_class = ProcedureRunFilterSet
    lookup_field = 'uuid'
    permission_classes = [UserPermission]
    queryset = ProcedureRun.objects.all()
    serializer_class = ProcedureRunSerializer
    serializer_class_mapping = {
        'create': ProcedureRunCreateSyncSerializer,
        'create_async': ProcedureRunCreateASyncSerializer,
    }

    def get_queryset(self):
        return super().get_queryset().filter(
            procedure__site__user__uuid=self.request.user.uuid)

    def get_serializer_class(self):
        return (
            self.serializer_class_mapping.get(self.action) or
            super().get_serializer_class()
        )

    def get_procedure(self):
        procedure = apps.get_model('editors.Procedure').objects.filter(
            site__user__uuid=self.request.user.uuid,
            **self.get_parents_query_dict_ex(ignore_prefix='procedure__')
        ).first()
        if not procedure:
            raise exceptions.NotFound('invalid procedure')
        return procedure

    def perform_create(self, serializer):
        return serializer.save(procedure=self.get_procedure())

    @decorators.action(
        methods=['post'],
        url_name='async',
        url_path='async',
        detail=False,
    )
    def create_async(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(procedure=self.get_procedure())

        return response.Response(
            serializer.data, status=status.HTTP_201_CREATED)


class ProcedureRunLogViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    filter_class = ProcedureRunLogFilterSet
    lookup_field = 'uuid'
    permission_classes = [UserPermission]
    queryset = ProcedureRun.objects.all()
    serializer_class = ProcedureRunLogSerializer

    def get_queryset(self):
        return super().get_queryset().filter(
            procedure__site__user__uuid=self.request.user.uuid)
