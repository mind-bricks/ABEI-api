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
    site = serializers.CharField(
        source='inner_procedure.site.signature',
        read_only=True,
    )
    procedure = serializers.CharField(
        source='inner_procedure.signature',
        read_only=True,
    )
    inputs = ProcedureJointInputSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = ProcedureJoint
        fields = [
            'signature',
            'site',
            'procedure',
            'inputs',
        ]


class ProcedureJointCreateSerializer(ProcedureJointSerializer):
    site = serializers.CharField(
        source='inner_procedure.site.signature',
    )
    procedure = serializers.CharField(
        source='inner_procedure.signature',
    )

    def create(self, validated_data):
        # get inner site
        inner_procedure = validated_data['inner_procedure']
        inner_site_signature = inner_procedure['site']['signature']

        # check dependencies
        outer_procedure = validated_data['outer_procedure']
        if not outer_procedure.site.base_sites.filter(
                signature=inner_site_signature
        ).exists():
            raise exceptions.ValidationError(
                'procedure of joint should be in base sites')

        # get inner procedure
        inner_procedure = Procedure.objects.filter(
            site__signature=inner_site_signature,
            signature=inner_procedure['signature'],
        ).first()
        if not inner_procedure:
            raise exceptions.ValidationError('invalid procedure')

        validated_data['inner_procedure'] = inner_procedure
        # create joint instance
        return super().create(validated_data)


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
        slug_field='signature',
        read_only=True,
    )

    site = serializers.SlugRelatedField(
        slug_field='signature',
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
            'site',
        ]
