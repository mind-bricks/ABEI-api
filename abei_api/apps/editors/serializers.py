from rest_framework import (
    exceptions,
    serializers,
)

from .models import (
    Procedure,
    ProcedureInput,
    ProcedureOutput,
    ProcedureOutputDetail,
    ProcedureJoint,
    ProcedureJointInput,
    ProcedureSite,
    ProcedureSiteRelationship,
)


class ProcedureJointInputSerializer(serializers.ModelSerializer):
    input_joint = serializers.SlugRelatedField(
        required=False,
        allow_null=True,
        default=None,
        slug_field='signature',
        queryset=ProcedureJoint.objects.all(),
    )

    class Meta:
        model = ProcedureJointInput
        fields = [
            'index',
            'input_joint',
            'input_index',
        ]

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        if (
                instance.input_joint and
                instance.joint.outer_procedure !=
                instance.input_joint.outer_procedure
        ):
            raise exceptions.ValidationError(
                'input of a joint should belong to '
                'the same procedure of this joint'
            )
        return instance


class ProcedureJointSerializer(serializers.ModelSerializer):
    procedure = serializers.SlugRelatedField(
        source='inner_procedure',
        slug_field='signature',
        queryset=Procedure.objects.all(),
    )
    inputs = ProcedureJointInputSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = ProcedureJoint
        fields = [
            'signature',
            'procedure',
            'inputs',
        ]

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        base_site = instance.inner_procedure.site
        base_sites = instance.outer_procedure.site.base_sites
        if base_site and not base_sites.filter(
                base_relations__base=base_site
        ).exists():
            raise exceptions.ValidationError(
                'procedure of joint should be in base sites')

        return instance


class ProcedureInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedureInput
        fields = [
            'signature',
            'index',
        ]


class ProcedureOutputDetailSerializer(serializers.ModelSerializer):
    output_joint = serializers.SlugRelatedField(
        slug_field='signature',
        allow_null=True,
        read_only=True,
    )

    class Meta:
        model = ProcedureOutputDetail
        fields = [
            'output_joint',
            'output_index',
        ]


class ProcedureOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedureOutput
        fields = [
            'signature',
            'index',
        ]


class ProcedureSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedureSite
        fields = [
            'signature',
        ]


class ProcedureSiteBaseSitesSerializer(serializers.ModelSerializer):
    signature = serializers.SlugRelatedField(
        source='base',
        slug_field='signature',
        queryset=ProcedureSite.objects.all(),
    )

    class Meta:
        model = ProcedureSiteRelationship
        fields = [
            'signature',
        ]


class ProcedureSerializer(serializers.ModelSerializer):
    inputs = ProcedureInputSerializer(
        many=True,
        read_only=True,
    )

    outputs = ProcedureOutputSerializer(
        many=True,
        read_only=True,
    )

    joints = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='signature',
    )

    site = serializers.SlugRelatedField(
        slug_field='signature',
        # allow_null=True,
        queryset=ProcedureSite.objects.all(),
    )

    class Meta:
        model = Procedure
        fields = [
            'signature',
            'docstring',
            'joints',
            'inputs',
            'outputs',
            'site',
        ]
