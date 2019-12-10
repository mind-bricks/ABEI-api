class AnonymousUser(object):
    id = None
    pk = None
    username = ''
    is_staff = False
    is_active = False
    is_superuser = False

    def __str__(self):
        return 'AnonymousUser'

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __hash__(self):
        return 1  # instances always return the same hash value

    # def __int__(self):
    #     raise TypeError()

    def save(self):
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()

    def set_password(self, raw_password):
        raise NotImplementedError()

    def check_password(self, raw_password):
        raise NotImplementedError()

    @property
    def groups(self):
        return []

    @property
    def user_permissions(self):
        return []

    def get_group_permissions(self, obj=None):
        return set()

    def get_all_permissions(self, obj=None):
        return False

    def has_perm(self, perm, obj=None):
        return False

    def has_perms(self, perm_list, obj=None):
        return False

    def has_module_perms(self, module):
        return False

    @property
    def is_anonymous(self):
        return True

    @property
    def is_authenticated(self):
        return False

    def get_username(self):
        return self.username
