from django.db import models


class ProcedureSite(models.Model):
    signature = models.CharField(
        max_length=128,
    )
    base_sites = models.ManyToManyField(
        'self',
        related_name='sub_sites',
        through='ProcedureSiteRelationship',
        symmetrical=False,
    )
    user = models.ForeignKey(
        'users.User',
        null=True,
        default=None,
        related_name='sites',
        on_delete=models.PROTECT,
        db_constraint=False,
    )

    class Meta:
        unique_together = [
            ('user', 'signature'),
        ]


class ProcedureSiteRelationship(models.Model):
    sub = models.ForeignKey(
        ProcedureSite,
        related_name='sub_relations',
        on_delete=models.CASCADE,
    )

    base = models.ForeignKey(
        ProcedureSite,
        related_name='base_relations',
        on_delete=models.PROTECT,
    )

    class Meta:
        unique_together = [
            ('base', 'sub')
        ]


class Procedure(models.Model):
    signature = models.CharField(
        max_length=128,
        # unique=True,
    )
    docstring = models.TextField(
        blank=True,
        default='',
    )
    site = models.ForeignKey(
        ProcedureSite,
        related_name='procedures',
        on_delete=models.PROTECT,
    )
    editable = models.BooleanField(
        default=True,
    )

    class Meta:
        unique_together = [
            ('site', 'signature'),
        ]


class ProcedureJoint(models.Model):
    outer_procedure = models.ForeignKey(
        Procedure,
        related_name='joints',
        on_delete=models.CASCADE,
    )
    inner_procedure = models.ForeignKey(
        Procedure,
        related_name='joint_references',
        on_delete=models.PROTECT,
    )
    signature = models.CharField(
        max_length=128,
    )

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
    )
    input_index = models.SmallIntegerField()
    joint = models.ForeignKey(
        ProcedureJoint,
        related_name='inputs',
        on_delete=models.CASCADE,
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
    )
    signature = models.CharField(
        max_length=128,
    )
    index = models.SmallIntegerField()

    class Meta:
        unique_together = [
            ('procedure', 'index'),
        ]


class ProcedureOutput(models.Model):
    procedure = models.ForeignKey(
        Procedure,
        related_name='outputs',
        on_delete=models.CASCADE,
    )
    signature = models.CharField(
        max_length=128,
    )
    index = models.SmallIntegerField()

    class Meta:
        unique_together = [
            ('procedure', 'index'),
        ]


class ProcedureOutputDetail(models.Model):
    output = models.OneToOneField(
        ProcedureOutput,
        related_name='detail',
        on_delete=models.CASCADE,
    )
    output_joint = models.ForeignKey(
        ProcedureJoint,
        null=True,
        related_name='output_references',
        on_delete=models.PROTECT,
    )
    output_index = models.SmallIntegerField()
