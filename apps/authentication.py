from uuid import UUID

from abei.interfaces import (
    IStorage,
    service_entry as _,
)
from django.apps import apps
from django.utils.functional import cached_property
from mb_drf_extensions import authentication

from .settings import (
    default_service_site
)
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
    """
    customized bearer authentication
    """

    @cached_property
    def builtin_user(self):
        storage = default_service_site.get_service(_(IStorage))
        access_token = storage.get_value(
            'builtin-user:access_token')

        if not access_token:
            return None

        username = storage.get_value(
            'builtin-user:username') or 'Builtin'

        return AuthenticatedUser({
            'uuid': str(UUID(int=1)),
            'username': username,
            'scopes': [scope_of_users],
        }, access_token=access_token)

    def authenticate(self, request):
        instance = super().authenticate(request)
        if not instance and self.builtin_user:
            return (
                self.builtin_user,
                self.builtin_user.access_token,
            )

        return instance

    def compose_user(self, user, access_token):
        return AuthenticatedUser(
            user,
            access_token=access_token,
        )
