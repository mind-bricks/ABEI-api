from rest_framework import (
    serializers,
)

from .models import (
    Procedure,
    ProcedureInput,
    ProcedureOutput,
    ProcedureJoint,
    ProcedureJointInput,
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
        ]


class ProcedureOutputSerializer(serializers.ModelSerializer):
    output_joint = serializers.SlugRelatedField(
        slug_field='signature',
        queryset=ProcedureJoint.objects.all(),
    )

    class Meta:
        model = ProcedureOutput
        fields = [
            'signature',
            'index',
            'output_joint',
            'output_index',
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

    class Meta:
        model = Procedure
        fields = [
            'signature',
            'docstring',
            'joints',
            'inputs',
            'outputs',
        ]
