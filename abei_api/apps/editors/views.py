from django.db import IntegrityError
from django.db.models import ProtectedError
from rest_framework import (
    decorators,
    exceptions,
    mixins,
    response,
    viewsets,
)

from ..mixins import (
    NestedViewSetMixin
)
from .filters import (
    ProcedureSiteFilterSet,
    ProcedureFilterSet,
)
from .models import (
    Procedure,
    ProcedureJoint,
    ProcedureJointInput,
    ProcedureInput,
    ProcedureOutput,
    ProcedureSite,
    ProcedureSiteRelationship,
)

from .serializers import (
    ProcedureSerializer,
    ProcedureJointSerializer,
    ProcedureJointCreateSerializer,
    ProcedureJointInputSerializer,
    ProcedureInputSerializer,
    ProcedureOutputSerializer,
    ProcedureOutputDetailSerializer,
    ProcedureSiteSerializer,
    ProcedureSiteBaseSitesSerializer,
)
from .utils import init_sites


class ProcedureSiteViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    filter_class = ProcedureSiteFilterSet
    lookup_field = 'signature'
    queryset = ProcedureSite.objects.all()
    serializer_class = ProcedureSiteSerializer

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError as e:
            raise exceptions.NotAcceptable(str(e))

    @decorators.action(
        methods=['post'],
        detail=False,
    )
    def init(self, request, *args, **kwargs):
        init_sites()
        return response.Response()


class ProcedureSiteBaseSitesViewSet(
    NestedViewSetMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = 'base__signature'
    queryset = ProcedureSiteRelationship.objects.all()
    serializer_class = ProcedureSiteBaseSitesSerializer

    def perform_create(self, serializer):
        site = ProcedureSite.objects.filter(
            **self.get_parents_query_dict_ex(
                ignore_prefix='sub__')
        ).first()

        if not site:
            raise exceptions.NotFound()

        try:
            serializer.save(sub=site)
        except IntegrityError as e:
            raise exceptions.NotAcceptable(str(e))


class ProcedureViewSet(
    NestedViewSetMixin,
    viewsets.ModelViewSet,
):
    filter_class = ProcedureFilterSet
    lookup_field = 'signature'
    queryset = Procedure.objects.all()
    serializer_class = ProcedureSerializer

    def perform_create(self, serializer):
        site = ProcedureSite.objects.filter(
            **self.get_parents_query_dict_ex(
                ignore_prefix='site__')
        ).first()

        if not site:
            raise exceptions.NotFound()

        try:
            serializer.save(site=site)
        except IntegrityError as e:
            raise exceptions.NotAcceptable(str(e))

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError as e:
            raise exceptions.NotAcceptable(str(e))


class ProcedureJointViewSet(
    NestedViewSetMixin,
    viewsets.ModelViewSet,
):
    lookup_field = 'signature'
    queryset = ProcedureJoint.objects.all()
    serializer_class = ProcedureJointSerializer

    def get_serializer_class(self):
        if self.action in ['create']:
            return ProcedureJointCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        outer_procedure = Procedure.objects.filter(
            **self.get_parents_query_dict_ex(
                ignore_prefix='outer_procedure__')
        ).first()

        if not outer_procedure:
            raise exceptions.NotFound()

        try:
            serializer.save(outer_procedure=outer_procedure)
        except IntegrityError as e:
            raise exceptions.NotAcceptable(str(e))


class ProcedureJointInputViewSet(
    NestedViewSetMixin,
    viewsets.ModelViewSet,
):
    lookup_field = 'index'
    queryset = ProcedureJointInput.objects.all()
    serializer_class = ProcedureJointInputSerializer

    def perform_create(self, serializer):
        input_joint = ProcedureJoint.objects.filter(
            **self.get_parents_query_dict_ex(
                ignore_prefix='joint__')
        ).first()
        if not input_joint:
            raise exceptions.NotFound()

        try:
            serializer.save(joint=input_joint)
        except IntegrityError as e:
            raise exceptions.NotAcceptable(str(e))

    def perform_destroy(self, instance):
        instance.delete()


class ProcedureInputViewSet(
    NestedViewSetMixin,
    viewsets.ModelViewSet,
):
    lookup_field = 'index'
    queryset = ProcedureInput.objects.all()
    serializer_class = ProcedureInputSerializer

    def perform_create(self, serializer):
        procedure = Procedure.objects.filter(
            **self.get_parents_query_dict_ex(
                ignore_prefix='procedure__')
        ).first()
        if not procedure:
            raise exceptions.NotFound()

        try:
            serializer.save(procedure=procedure)
        except IntegrityError as e:
            raise exceptions.ValidationError(str(e))

    def perform_destroy(self, instance):
        instance.delete()


class ProcedureOutputViewSet(
    NestedViewSetMixin,
    viewsets.ModelViewSet,
):
    lookup_field = 'index'
    queryset = ProcedureOutput.objects.select_related('detail').all()
    serializer_class = ProcedureOutputSerializer

    def perform_create(self, serializer):
        procedure = Procedure.objects.filter(
            **self.get_parents_query_dict_ex(
                ignore_prefix='procedure__')
        ).first()

        if not procedure:
            raise exceptions.NotFound()

        try:
            serializer.save(procedure=procedure)
        except IntegrityError as e:
            raise exceptions.ValidationError(str(e))

    def perform_destroy(self, instance):
        instance.delete()

    @decorators.action(
        url_name='detail',
        url_path='detail',
        detail=False,
        serializer_class=ProcedureOutputDetailSerializer,
    )
    def detail(self, request):
        instance = self.get_object()
        instance = getattr(instance, 'detail', None)
        if not instance:
            raise exceptions.NotFound()
        serializer = self.get_serializer(instance=instance)
        return response.Response(serializer.data)

    @detail.mapping.put
    def set_detail(self, request):
        instance_base = self.get_object()
        instance = getattr(instance_base, 'detail', None)
        serializer = self.get_serializer(
            instance=instance, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(output=instance_base)
        return response.Response(serializer.data)
