from rest_framework import (
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
        allow_null=True,
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

    site = serializers.SlugRelatedField(
        slug_field='signature',
        allow_null=True,
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
