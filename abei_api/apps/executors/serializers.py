import json

from django.apps import apps
from django.utils import timezone
from rest_framework import (
    serializers,
)

from .models import (
    ProcedureRun,
)
from .tasks import (
    load_procedure,
    load_and_run_procedure,
    run_procedure,
)


class ProcedureRunSerializer(serializers.ModelSerializer):
    procedure = serializers.SlugRelatedField(
        slug_field='signature',
        queryset=apps.get_model('editors.Procedure').objects.all(),
    )
    outputs = serializers.SerializerMethodField()

    class Meta:
        model = ProcedureRun
        fields = [
            'uuid',
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
            'outputs',
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
    inputs = serializers.ListField(
        write_only=True,
        required=False,
    )

    class Meta(ProcedureRunSerializer.Meta):
        fields = [
            'inputs',
            *ProcedureRunSerializer.Meta.fields
        ]


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
