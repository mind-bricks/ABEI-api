from rest_framework_extensions import mixins


class NestedViewSetMixin(mixins.NestedViewSetMixin):

    def get_parents_query_dict_ex(self, ignore_prefix=None):
        if not ignore_prefix:
            return self.get_parents_query_dict()

        return {
            (
                k[len(ignore_prefix):] if
                k.startswith(ignore_prefix) else k
            ): v for k, v in self.get_parents_query_dict().items()
        }
