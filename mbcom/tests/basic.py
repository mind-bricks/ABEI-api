from unittest import TestCase

from mbcom.implements import (
    ServiceSite,
    ServiceBuilder,
)


class TestCaseBasic(TestCase):
    service_site = ServiceSite()
    service_config_files = []

    @classmethod
    def setUpClass(cls):
        builder = ServiceBuilder()
        for filename in cls.service_config_files:
            builder.load_yaml(cls.service_site, filename)
