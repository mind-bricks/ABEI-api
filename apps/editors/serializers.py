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
    input_joint = serializers.CharField(
        source='input_joint.signature',
        read_only=True,
    )

    class Meta:
        model = ProcedureJointInput
        fields = [
            'index',
            'input_joint',
            'input_index',
        ]


class ProcedureJointInputCreateSerializer(
    ProcedureJointInputSerializer
):
    input_joint = serializers.CharField(
        source='input_joint.signature',
        allow_null=True,
        default=None,
        required=False,
    )

    def create(self, validated_data):
        # get input joint
        joint_signature = validated_data['input_joint']['signature']
        if not joint_signature:
            validated_data['input_joint'] = None
            # create joint input directly accept input from outer procedure
            return super().create(validated_data)

        input_joint = ProcedureJoint.objects.filter(
            signature=joint_signature,
            outer_procedure=validated_data['joint'].outer_procedure,
        ).first()

        if not input_joint:
            raise exceptions.ValidationError('invalid input joint')

        # fill up extra fields and create joint input instance
        validated_data['input_joint'] = input_joint
        return super().create(validated_data)


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
        user_uuid = validated_data.pop('user_uuid')
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
            site__user__uuid=user_uuid,
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


class ProcedureSiteCreateSerializer(ProcedureSiteSerializer):
    base_sites = ProcedureSiteSerializer(
        many=True,
        required=False,
    )

    class Meta(ProcedureSiteSerializer.Meta):
        fields = [
            'base_sites',
            *ProcedureSiteSerializer.Meta.fields,
        ]

    def create(self, validated_data):
        # TODO: avoid recursive dependencies

        base_sites = validated_data.pop('base_sites', [])
        base_sites = ProcedureSite.objects.filter(
            user=validated_data['user'],
            signature__in=[s['signature'] for s in base_sites],
        ).all()

        instance = super().create(validated_data)
        instance.base_sites.add(*base_sites)
        return instance


class ProcedureSiteBaseSitesSerializer(serializers.ModelSerializer):
    signature = serializers.CharField(
        source='base.signature',
        read_only=True,
    )

    class Meta:
        model = ProcedureSiteRelationship
        fields = [
            'signature',
        ]


class ProcedureSiteBaseSitesCreateSerializer(
    ProcedureSiteBaseSitesSerializer
):
    signature = serializers.CharField(
        source='base.signature',
    )

    def create(self, validated_data):
        # get base site
        user_uuid = validated_data.pop('user_uuid')
        site = ProcedureSite.objects.filter(
            user__uuid=user_uuid,
            signature=validated_data['base']['signature']
        ).first()

        if not site:
            raise exceptions.ValidationError('invalid base site')

        # TODO: avoid recursive dependencies

        # fill up missing fields and create site relationship
        validated_data['base'] = site
        return super().create(validated_data)


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
            'inputs',
            'outputs',
            'joints',
            'site',
            'editable',
        ]
        read_only_fields = [
            'inputs',
            'outputs',
            'joints',
            'site',
            'editable',
        ]
