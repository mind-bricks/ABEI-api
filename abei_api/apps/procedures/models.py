from django.db import models


class Procedure(models.Model):
    signature = models.CharField(max_length=128, unique=True)
    docstring = models.TextField(blank=True, default='')


class ProcedureJoint(models.Model):
    outer_procedure = models.ForeignKey(
        Procedure,
        related_name='joints',
        on_delete=models.CASCADE,
        db_constraint=False,
    )
    inner_procedure = models.ForeignKey(
        Procedure,
        related_name='joint_references',
        on_delete=models.PROTECT,
        db_constraint=False,
    )
    signature = models.CharField(max_length=128)

    class Meta:
        unique_together = [
            ('outer_procedure', 'signature'),
        ]


class ProcedureJointInput(models.Model):
    input_joint = models.ForeignKey(
        ProcedureJoint,
        null=True,
        related_name='input_references',
        on_delete=models.PROTECT,
        db_constraint=False,
    )
    input_index = models.SmallIntegerField()
    joint = models.ForeignKey(
        ProcedureJoint,
        related_name='inputs',
        on_delete=models.CASCADE,
        db_constraint=False,
    )
    index = models.SmallIntegerField()

    class Meta:
        unique_together = [
            ('joint', 'index'),
        ]


class ProcedureInput(models.Model):
    procedure = models.ForeignKey(
        Procedure,
        related_name='inputs',
        on_delete=models.CASCADE,
        db_constraint=False,
    )
    signature = models.CharField(max_length=128)
    # sort = models.SmallIntegerField(default=0)


class ProcedureOutput(models.Model):
    procedure = models.ForeignKey(
        Procedure,
        related_name='outputs',
        on_delete=models.CASCADE,
        db_constraint=False,
    )
    signature = models.CharField(max_length=128)
    # sort = models.SmallIntegerField(default=0)
    output_joint = models.ForeignKey(
        ProcedureJoint,
        related_name='output_references',
        on_delete=models.PROTECT,
        db_constraint=False,
    )
    output_index = models.SmallIntegerField()
    index = models.SmallIntegerField()

    class Meta:
        unique_together = [
            ('procedure', 'index'),
        ]
