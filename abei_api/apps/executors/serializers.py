import json

from django.apps import apps
from django.utils import timezone
from rest_framework import (
    exceptions,
    serializers,
)

from .models import (
    ProcedureRun,
)
from .tasks import (
    load_procedure,
    # load_and_run_procedure,
    run_procedure,
)


class ProcedureRunSerializer(serializers.ModelSerializer):
    site = serializers.CharField(
        source='procedure.site.signature',
        read_only=True,
    )
    procedure = serializers.CharField(
        source='procedure.signature',
        read_only=True,
    )
    outputs = serializers.SerializerMethodField()

    class Meta:
        model = ProcedureRun
        fields = [
            'uuid',
            'site',
            'procedure',
            'status',
            'created_time',
            'finished_time',
            'outputs',
        ]
        read_only_fields = [
            'uuid',
            'status',
            'created_time',
            'finished_time',
        ]

    @staticmethod
    def get_outputs(instance):
        try:
            outputs = json.loads(instance.outputs)
            assert isinstance(outputs, (list, tuple))
            return outputs
        except (ValueError, KeyError, AssertionError):
            return None


class ProcedureRunCreateSerializer(ProcedureRunSerializer):
    site = serializers.CharField(
        source='procedure.site.signature',
    )
    procedure = serializers.CharField(
        source='procedure.signature',
    )
    inputs = serializers.ListField(
        write_only=True,
        required=False,
    )

    class Meta(ProcedureRunSerializer.Meta):
        fields = [
            'inputs',
            *ProcedureRunSerializer.Meta.fields
        ]

    def validate(self, attrs):
        # get procedure instance
        procedure = attrs['procedure']
        procedure = apps.get_model('editors.Procedure').objects.filter(
            site__signature=procedure['site']['signature'],
            signature=procedure['signature'],
        ).first()
        if not procedure:
            raise exceptions.ValidationError('invalid procedure')

        # update procedure attribute
        attrs['procedure'] = procedure
        return attrs


class ProcedureRunCreateSyncSerializer(ProcedureRunCreateSerializer):

    def create(self, validated_data):
        outputs = run_procedure(
            load_procedure(validated_data['procedure']),
            validated_data.pop('inputs', []),
        )
        outputs = [o.get_value() for o in outputs]
        validated_data.update(
            status='finished',
            finished_time=timezone.now(),
            outputs=json.dumps(outputs),
        )
        return super().create(validated_data)


class ProcedureRunCreateASyncSerializer(ProcedureRunCreateSerializer):

    def create(self, validated_data):
        raise NotImplementedError
        # inputs = validated_data.pop('inputs', [])
        # instance = super().create(validated_data)
        #
        # return instance
