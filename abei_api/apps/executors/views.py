from rest_framework import (
    decorators,
    mixins,
    response,
    status,
    viewsets,
)

from .filters import (
    ProcedureRunFilterSet,
)
from .models import (
    ProcedureRun,
)
from .serializers import (
    ProcedureRunSerializer,
    ProcedureRunCreateSyncSerializer,
    ProcedureRunCreateASyncSerializer,
)


class ProcedureRunViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    filter_class = ProcedureRunFilterSet
    lookup_field = 'uuid'
    queryset = ProcedureRun.objects.all()
    serializer_class = ProcedureRunSerializer
    serializer_class_mapping = {
        'create': ProcedureRunCreateSyncSerializer,
        'create_async': ProcedureRunCreateASyncSerializer,
    }

    def get_serializer_class(self):
        return (
            self.serializer_class_mapping.get(self.action) or
            super().get_serializer_class()
        )

    @decorators.action(
        methods=['post'],
        url_name='async',
        url_path='async',
        detail=False,
    )
    def create_async(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(
            serializer.data, status=status.HTTP_201_CREATED)
