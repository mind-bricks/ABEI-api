from .service import (
    abstractmethod,
    IService,
)


class ProcedureException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ProcedureBreakPoint(ProcedureException):
    def __init__(self):
        super().__init__('break point')


class ProcedureSignature(object):
    def __init__(self, name, label):
        self.name = name  # can be any type
        self.label = label

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name

    def __str__(self):
        return str(self.name)


class IProcedureData(IService):

    @abstractmethod
    def get_signature(self):
        """
        get signature of procedure data
        :return:
        """

    @abstractmethod
    def dump(self):
        """
        dump procedure data for debug use
        :return:
        """


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
    def set_joints(self, output_flows, output_indices):
        """
        set procedure flow joints
        :param output_flows:
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


class IProcedureFlow(IService):
    @abstractmethod
    def get_signature(self):
        """
        get signature of procedure flow
        :return:
        """

    @abstractmethod
    def get_joints(self):
        """
        get procedure flow joints
        :return: list of procedure flow and index pair
        """

    @abstractmethod
    def set_joints(self, input_flows, input_indices):
        """
        set procedure flow joints
        :param input_flows:
        :param input_indices:
        :return:
        """

    @abstractmethod
    def get_inner_procedure(self):
        """
        get inner procedure of current flow
        :return:
        """

    @abstractmethod
    def get_outer_procedure(self):
        """
        get outer procedure of current flow
        :return:
        """

    @abstractmethod
    def get_breakpoint(self):
        """
        get if breakpoint is set
        :return:
        """

    @abstractmethod
    def set_breakpoint(self, is_breakpoint):
        """
        set breakpoint or not
        :param is_breakpoint:
        :return:
        """


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
    def register_procedure(self, procedure):
        """
        register procedure
        """


class IProcedureConfiguration(IService):

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
