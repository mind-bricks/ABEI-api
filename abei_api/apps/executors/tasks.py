import json
import time

from django.utils import timezone
from rest_framework import exceptions

from .builders import (
    default_procedure_builder,
    default_procedure_data_builder,
)
from .models import ProcedureRun


def load_procedure(procedure):
    try:
        procedure_object = default_procedure_builder.load_model(procedure)
        if not procedure_object:
            raise exceptions.ValidationError('failed to load procedure')

    except exceptions.APIException as e:
        raise e

    except Exception as e:
        raise exceptions.ValidationError('load error: {}'.format(str(e)))

    return procedure_object


def run_procedure(procedure_object, inputs):
    try:
        input_signatures = procedure_object.get_input_signatures()
        if len(inputs) != len(input_signatures):
            raise exceptions.ValidationError('invalid inputs')
        inputs = [
            default_procedure_data_builder.create(sig, value=i)
            for i, sig in zip(inputs, input_signatures)
        ]

        if None in inputs:
            raise exceptions.ValidationError('invalid inputs')

        return procedure_object.run(inputs)

    except exceptions.APIException as e:
        raise e

    except Exception as e:
        raise exceptions.APIException('run error: {}'.format(str(e)))


def load_and_run_procedure(run_uuid, inputs):
    def get_procedure_run(run_uuid_):
        for _ in range(3):
            try:
                return ProcedureRun.objects.select_related(
                    'procedure'
                ).get(uuid=run_uuid_)

            except Exception as err:
                print(err)
                time.sleep(1)  # sleep for a while

    run = get_procedure_run(run_uuid)
    if not run:
        return

    run.status = 'running'
    run.save(update_fields=['status'])

    try:
        outputs = run_procedure(
            load_procedure(run.procedure), inputs)

    except Exception as e:
        run.status = 'finished'
        run.finished_time = timezone.now()
        run.errors = str(e)
        run.save(update_fields=['status', 'finished_time', 'errors'])
        return

    outputs = [o.get_value() for o in outputs]
    run.status = 'finished'
    run.finished_time = timezone.now()
    run.outputs = json.dumps(outputs)
    run.save(update_fields=['status', 'finished_time', 'outputs'])
