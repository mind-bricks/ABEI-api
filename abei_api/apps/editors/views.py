from django.db import IntegrityError
from django.db.models import ProtectedError
from rest_framework import (
    decorators,
    exceptions,
    mixins,
    response,
    viewsets,
)

from rest_framework_extensions.mixins import (
    NestedViewSetMixin,
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
    ProcedureJointInputSerializer,
    ProcedureInputSerializer,
    ProcedureOutputSerializer,
    ProcedureOutputDetailSerializer,
    ProcedureSiteSerializer,
    ProcedureSiteBaseSitesSerializer,
)


class ProcedureSiteViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = 'signature'
    queryset = ProcedureSite.objects.all()
    serializer_class = ProcedureSiteSerializer

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError:
            raise exceptions.NotAcceptable()


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
            signature=self.kwargs.get(
                'parent_lookup_sub__signature')).first()
        if not site:
            raise exceptions.NotFound()

        try:
            serializer.save(sub=site)
        except IntegrityError:
            raise exceptions.NotAcceptable()


class ProcedureViewSet(
    viewsets.ModelViewSet,
):
    lookup_field = 'signature'
    queryset = Procedure.objects.all()
    serializer_class = ProcedureSerializer


class ProcedureJointViewSet(
    NestedViewSetMixin,
    viewsets.ModelViewSet,
):
    lookup_field = 'signature'
    queryset = ProcedureJoint.objects.all()
    serializer_class = ProcedureJointSerializer

    def perform_create(self, serializer):
        outer_procedure = Procedure.objects.filter(
            signature=self.kwargs.get(
                'parent_lookup_outer_procedure__signature')
        ).first()
        if not outer_procedure:
            raise exceptions.NotFound()
        serializer.save(outer_procedure=outer_procedure)


class ProcedureJointInputViewSet(
    NestedViewSetMixin,
    viewsets.ModelViewSet,
):
    lookup_field = 'index'
    queryset = ProcedureJointInput.objects.all()
    serializer_class = ProcedureJointInputSerializer

    def perform_create(self, serializer):
        # todo: ???
        input_joint = ProcedureJoint.objects.filter(
            signature=self.kwargs.get(
                'parent_lookup_input_joint__signature'),
            outer_procedure__signature=self.kwargs.get(
                'parent_lookup_joint__outer_procedure__signature'),
        ).first()
        if not input_joint:
            raise exceptions.NotFound()
        serializer.save(input_joint=input_joint)

    def perform_destroy(self, instance):
        # todo:
        instance.delete()


class ProcedureInputViewSet(
    NestedViewSetMixin,
    viewsets.ModelViewSet,
):
    lookup_field = 'index'
    queryset = ProcedureInput.objects.all()
    serializer_class = ProcedureInputSerializer

    def perform_create(self, serializer):
        # todo:
        serializer.save()

    def perform_destroy(self, instance):
        # todo:
        instance.delete()


class ProcedureOutputViewSet(
    NestedViewSetMixin,
    viewsets.ModelViewSet,
):
    lookup_field = 'index'
    queryset = ProcedureOutput.objects.select_related('detail').all()
    serializer_class = ProcedureOutputSerializer

    def perform_create(self, serializer):
        # todo:
        serializer.save()

    def perform_destroy(self, instance):
        # todo:
        instance.delete()

    @decorators.action(
        methods=['put', 'get'],
        detail=False,
        serializer_class=ProcedureOutputDetailSerializer,
    )
    def detail(self, request):
        detail_method_name = '{}_detail'.format(request.method.lower())
        detail_method = getattr(self, detail_method_name, None)
        if not detail_method:
            raise exceptions.NotFound()
        return detail_method(request)

    def put_detail(self, request):
        instance_base = self.get_object()
        instance = getattr(instance_base, 'detail', None)
        serializer = self.get_serializer(
            instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(output=instance_base)
        return response.Response(serializer.data)

    def get_detail(self, request):
        instance = self.get_object()
        instance = getattr(instance, 'detail', None)
        if not instance:
            raise exceptions.NotFound()
        serializer = self.get_serializer(instance=instance)
        return response.Response(serializer.data)
