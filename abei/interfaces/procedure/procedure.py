from ..service import (
    abstractmethod,
    IService,
)


class IProcedure(IService):

    @abstractmethod
    def get_signature(self):
        """
        get signature of procedure
        :return:
        """

    @abstractmethod
    def get_input_signatures(self):
        """
        get list of input signatures
        :return:
        """

    @abstractmethod
    def get_output_signatures(self):
        """
        get list of output signatures
        :return:
        """

    @abstractmethod
    def get_docstring(self):
        """
        get document string of procedure
        :return:
        """

    @abstractmethod
    def set_docstring(self, docstring):
        """
        set document string of procedure
        :param docstring:
        :return:
        """

    @abstractmethod
    def get_joints(self):
        """
        get procedure flow joints
        :return: list of procedure flow and index pair
        """

    @abstractmethod
    def set_joints(self, output_joints, output_indices):
        """
        set procedure flow joints
        :param output_joints:
        :param output_indices:
        :return:
        """

    @abstractmethod
    def run(self, procedure_data_list, **kwargs):
        """
        :param procedure_data_list: input code data list
        :param kwargs: extra arguments
        :return output code data list:
        """


class IProcedureFactory(IService):

    @abstractmethod
    def create(self, signature, **kwargs):
        """
        create procedure
        :param signature:
        :param kwargs:
        :return:
        """

    @abstractmethod
    def register_class(self, signature, procedure_class, **kwargs):
        """
        register procedure class
        :param signature:
        :param procedure_class:
        :param kwargs:
        :return:
        """

    @abstractmethod
    def iterate_classes(self):
        """
        iterate procedure classes
        :return:
        """
