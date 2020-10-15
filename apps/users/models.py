from django.db import models


class User(models.Model):
    uuid = models.UUIDField(
        unique=True,
    )
    created_time = models.DateTimeField(
        auto_now_add=True,
    )
    modified_time = models.DateTimeField(
        auto_now=True,
    )
