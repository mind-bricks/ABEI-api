from uuid import uuid1

from django.db import models


class ProcedureRun(models.Model):
    uuid = models.UUIDField(
        unique=True,
        default=uuid1,
    )
    procedure = models.ForeignKey(
        'editors.Procedure',
        related_name='runs',
        on_delete=models.CASCADE,
        db_constraint=False,
    )
    status_enum = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('finished', 'Finished'),
    ]
    status = models.CharField(
        max_length=16,
        choices=status_enum,
        default=status_enum[0][0],
    )
    created_time = models.DateTimeField(
        auto_now_add=True,
    )
    finished_time = models.DateTimeField(
        null=True,
        default=None,
    )
    outputs = models.TextField(
        null=True,
        default=None,
    )
    errors = models.TextField(
        null=True,
        default=None,
    )
