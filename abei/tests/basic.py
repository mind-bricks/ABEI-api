import os
from unittest import TestCase

from abei.implements import (
    ServiceSite,
    ServiceBuilder,
)


class TestCaseBasic(TestCase):
    service_site = ServiceSite()
    service_config_files = []
    service_config_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        'fixtures',
    ))

    @classmethod
    def setUpClass(cls):
        builder = ServiceBuilder()
        builder.ensure_dependencies()
        for filename in cls.service_config_files:
            builder.load_yaml(cls.service_site, (
                os.path.isabs(filename) and
                filename or
                os.path.join(cls.service_config_dir, filename)
            ))
