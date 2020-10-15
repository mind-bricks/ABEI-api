from mb_drf_extensions import permissions

from .scopes import (
    scope_of_admin,
    scope_of_users,
)


class AdminPermission(permissions.ScopesPermission):
    def get_scopes(self, request, view):
        return [scope_of_admin]


class UserPermission(permissions.ScopesPermission):
    def get_scopes(self, request, view):
        return [scope_of_users]
