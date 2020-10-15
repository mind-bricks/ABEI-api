import os

from django.conf import settings
from django.utils.functional import LazyObject

from abei.implements import (
    ServiceSite,
    ServiceBuilder,
)


class DefaultServiceSite(LazyObject):

    def _setup(self):
        components_filename = getattr(
            settings,
            'ABEI_API_SERVICE_SITE_CONFIG',
            os.path.join(
                os.path.dirname(__file__),
                os.pardir,
                'settings',
                'service_site.yml',
            ),
        )

        os.environ.setdefault(
            'CONFIG_FILE',
            os.path.join(
                os.path.dirname(__file__),
                os.pardir,
                'settings',
                'configs.yml',
            )
        )

        service_site = ServiceSite()
        service_site.ensure_dependencies()

        service_config = ServiceBuilder()
        service_config.ensure_dependencies()

        service_config.load_yaml(
            service_site, components_filename)

        self._wrapped = service_site


default_service_site = DefaultServiceSite()
