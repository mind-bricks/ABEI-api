from django.apps import apps
from mb_drf_extensions import authentication

from .scopes import (
    scope_of_admin,
    scope_of_users,
)


class AnonymousUser(authentication.AnonymousUser):
    """
    customized anonymous user
    """


class AuthenticatedUser(authentication.AuthenticatedUser):
    """
    customized authenticated user
    """

    @property
    def is_admin(self):
        return scope_of_admin in self.scopes

    @property
    def is_user(self):
        return scope_of_users in self.scopes

    def user_persist(self):
        if not self.is_user:
            return None

        instance, _ = apps.get_model(
            'users.User'
        ).objects.get_or_create(uuid=self.uuid)

        return instance


class BearerAuthentication(authentication.BearerAuthentication):
    def compose_user(self, user, access_token):
        return AuthenticatedUser(
            user,
            access_token=access_token,
        )
