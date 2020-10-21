from django.db import (
    IntegrityError,
    models,
)
from rest_framework import (
    decorators,
    exceptions,
    mixins,
    permissions,
    response,
    viewsets,
)

from ..mixins import (
    NestedViewSetMixin,
)
from ..permissions import (
    UserPermission,
)

from .filters import (
    ProcedureSiteFilterSet,
    ProcedureFilterSet,
)
from .models import (
    Procedure,
    ProcedureJoint,
    ProcedureJointLink,
    ProcedureInput,
    ProcedureOutput,
    ProcedureOutputLink,
    ProcedureSite,
    ProcedureSiteRelationship,
)

from .serializers import (
    ProcedureSerializer,
    ProcedureJointSerializer,
    ProcedureJointCreateSerializer,
    ProcedureJointLinkSerializer,
    ProcedureJointLinkCreateSerializer,
    ProcedureInputSerializer,
    ProcedureOutputSerializer,
    ProcedureOutputLinkSerializer,
    ProcedureSiteSerializer,
    ProcedureSiteCreateSerializer,
    ProcedureSiteBaseSitesSerializer,
    ProcedureSiteBaseSitesCreateSerializer,
)
from .utils import init_sites


class ProcedureSiteViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    filter_class = ProcedureSiteFilterSet
    lookup_field = 'signature'
    permission_classes = [UserPermission]
    queryset = ProcedureSite.objects.all()
    serializer_class = ProcedureSiteSerializer

    def get_queryset(self):
        return super().get_queryset().filter(
            user__uuid=self.request.user.uuid)

    def get_serializer_class(self):
        if self.action in ['create']:
            return ProcedureSiteCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.user_persist())

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except models.ProtectedError as e:
            raise exceptions.PermissionDenied(str(e))

    @decorators.action(
        methods=['post'],
        detail=False,
    )
    def init(self, request, *args, **kwargs):
        init_sites(user=self.request.user.user_persist())
        return response.Response()


class ProcedureSiteBaseSitesViewSet(
    NestedViewSetMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = 'base__signature'
    permission_classes = [UserPermission]
    queryset = ProcedureSiteRelationship.objects.all()
    serializer_class = ProcedureSiteBaseSitesSerializer

    def get_queryset(self):
        return super().get_queryset().filter(
            base__user__uuid=self.request.user.uuid,
            sub__user__uuid=self.request.user.uuid,
        )

    def get_serializer_class(self):
        if self.action in ['create']:
            return ProcedureSiteBaseSitesCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        site = ProcedureSite.objects.filter(
            user__uuid=self.request.user.uuid,
            **self.get_parents_query_dict_ex(
                ignore_prefix='sub__')
        ).first()

        if not site:
            raise exceptions.NotFound('invalid site')

        try:
            serializer.save(
                user_uuid=self.request.user.uuid,
                sub=site,
            )
        except IntegrityError as e:
            raise exceptions.PermissionDenied(str(e))

    def perform_destroy(self, instance):
        if ProcedureJoint.objects.filter(
                outer_procedure__site_id=instance.sub_id,
                inner_procedure__site_id=instance.base_id,
        ).exists():
            raise exceptions.PermissionDenied(
                'can not delete base site while it\'s being referenced')

        instance.delete()


class ProcedureViewSet(
    NestedViewSetMixin,
    viewsets.ModelViewSet,
):
    filter_class = ProcedureFilterSet
    lookup_field = 'signature'
    permission_classes = [UserPermission]
    queryset = Procedure.objects.prefetch_related(
        'inputs',
        'outputs',
    ).all()
    serializer_class = ProcedureSerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(
            site__user__uuid=self.request.user.uuid)

        if self.request.method in permissions.SAFE_METHODS:
            return qs

        return qs.filter(editable=True)

    def perform_create(self, serializer):
        site = ProcedureSite.objects.filter(
            user__uuid=self.request.user.uuid,
            **self.get_parents_query_dict_ex(
                ignore_prefix='site__')
        ).first()

        if not site:
            raise exceptions.NotFound()

        try:
            serializer.save(site=site)
        except IntegrityError as e:
            raise exceptions.PermissionDenied(str(e))

    def perform_destroy(self, instance):
        try:
            # try delete outputs first, for they may
            # prevent output joints from being deleted.
            # and with those joints, the owner procedure is
            # unable to be deleted either.
            instance.outputs.all().delete()
            instance.delete()
        except models.ProtectedError as e:
            raise exceptions.PermissionDenied(str(e))


class ProcedureJointViewSet(
    NestedViewSetMixin,
    viewsets.ModelViewSet,
):
    lookup_field = 'signature'
    permission_classes = [UserPermission]
    queryset = ProcedureJoint.objects.all()
    serializer_class = ProcedureJointSerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(
            outer_procedure__site__user__uuid=self.request.user.uuid
        )
        if self.request.method in permissions.SAFE_METHODS:
            return qs

        return qs.filter(outer_procedure__editable=True)

    def get_serializer_class(self):
        if self.action in ['create']:
            return ProcedureJointCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        outer_procedure = Procedure.objects.filter(
            site__user__uuid=self.request.user.uuid,
            editable=True,
            **self.get_parents_query_dict_ex(
                ignore_prefix='outer_procedure__')
        ).first()

        if not outer_procedure:
            raise exceptions.NotFound()

        try:
            serializer.save(
                user_uuid=self.request.user.uuid,
                outer_procedure=outer_procedure,
            )
        except IntegrityError as e:
            raise exceptions.PermissionDenied(str(e))

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except models.ProtectedError as e:
            raise exceptions.PermissionDenied(str(e))


class ProcedureJointLinkViewSet(
    NestedViewSetMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = 'index'
    permission_classes = [UserPermission]
    queryset = ProcedureJointLink.objects.all()
    serializer_class = ProcedureJointLinkSerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(
            joint__outer_procedure__site__user__uuid=self.request.user.uuid)

        if self.request.method in permissions.SAFE_METHODS:
            return qs

        return qs.filter(joint__outer_procedure__editable=True)

    def get_serializer_class(self):
        if self.action in ['create']:
            return ProcedureJointLinkCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        joint = ProcedureJoint.objects.filter(
            outer_procedure__site__user__uuid=self.request.user.uuid,
            outer_procedure__editable=True,
            **self.get_parents_query_dict_ex(
                ignore_prefix='joint__'),
        ).select_related('outer_procedure').first()

        if not joint:
            raise exceptions.NotFound('invalid procedure joint')

        try:
            serializer.save(joint=joint)

        except IntegrityError as e:
            raise exceptions.PermissionDenied(str(e))


class ProcedureInputViewSet(
    NestedViewSetMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = 'index'
    permission_classes = [UserPermission]
    queryset = ProcedureInput.objects.all()
    serializer_class = ProcedureInputSerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(
            procedure__site__user__uuid=self.request.user.uuid)

        if self.request.method in permissions.SAFE_METHODS:
            return qs

        return qs.filter(procedure__editable=True)

    def perform_create(self, serializer):
        procedure = Procedure.objects.filter(
            site__user__uuid=self.request.user.uuid,
            editable=True,
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
        if ProcedureJointLink.objects.filter(
                joint__inner_procedure_id=instance.procedure_id,
                index=instance.index,
        ).exists():
            raise exceptions.PermissionDenied(
                'can not delete input while its being referenced')

        instance.delete()


class ProcedureOutputViewSet(
    NestedViewSetMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = 'index'
    permission_classes = [UserPermission]
    queryset = ProcedureOutput.objects.select_related(
        'procedure',
        'output_link',
    ).all()
    serializer_class = ProcedureOutputSerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(
            procedure__site__user__uuid=self.request.user.uuid)

        if self.request.method in permissions.SAFE_METHODS:
            return qs

        return qs.filter(procedure__editable=True)

    def perform_create(self, serializer):
        procedure = Procedure.objects.filter(
            site__user__uuid=self.request.user.uuid,
            editable=True,
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
        if (
                ProcedureJointLink.objects.filter(
                    input_joint__inner_procedure_id=instance.procedure_id,
                    input_index=instance.index,
                ).exists() or

                ProcedureOutputLink.objects.filter(
                    output_joint__inner_procedure_id=instance.procedure_id,
                    output_index=instance.index,
                ).exists()
        ):
            raise exceptions.PermissionDenied(
                'can not delete output while its being referenced')

        instance.delete()

    @decorators.action(
        url_name='link',
        url_path='link',
        detail=True,
        permission_classes=[UserPermission],
        serializer_class=ProcedureOutputLinkSerializer,
    )
    def link(self, request, *args, **kwargs):
        instance = self.get_object()
        instance = getattr(instance, 'output_link', None)
        if not instance:
            raise exceptions.NotFound()

        serializer = self.get_serializer(instance=instance)
        return response.Response(serializer.data)

    @link.mapping.put
    def set_link(self, request, *args, **kwargs):
        instance_base = self.get_object()
        instance = getattr(instance_base, 'output_link', None)
        serializer = self.get_serializer(
            instance=instance,
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(
            output=instance_base,
        )
        return response.Response(serializer.data)
