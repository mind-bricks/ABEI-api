from .procedure import (
    abstractmethod,
    IService,
)


class IProcedureSite(IService):

    @abstractmethod
    def get_procedure(self, signature):
        """
        get procedure instance by signature
        raise exception if no service found
        """

    @abstractmethod
    def query_procedure(self, signature):
        """
        query procedure instance by signature
        """

    @abstractmethod
    def register_procedure(self, procedure, **kwargs):
        """
        register procedure
        """


class IProcedureSiteConfiguration(IService):

    @abstractmethod
    def load_json(self, procedure_site, file_or_filename):
        """
        :param procedure_site:
        :param file_or_filename:
        :return:
        """

    @abstractmethod
    def save_json(self, procedure_site, file_or_filename):
        """
        :param procedure_site:
        :param file_or_filename:
        :return:
        """

    @abstractmethod
    def load_yaml(self, procedure_site, file_or_filename):
        """
        :param procedure_site:
        :param file_or_filename:
        :return:
        """

    @abstractmethod
    def save_yaml(self, procedure_site, file_or_filename):
        """
        :param procedure_site:
        :param file_or_filename:
        :return:
        """
