from .procedure import (
    abstractmethod,
    IService,
)


class IProcedureJoint(IService):
    @abstractmethod
    def get_signature(self):
        """
        get signature of procedure joint
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

    @abstractmethod
    def get_joints(self):
        """
        get dependent joints
        :return: list of procedure flow and index pair
        """

    @abstractmethod
    def set_joints(self, input_joints, input_indices):
        """
        set dependent joints
        :param input_joints:
        :param input_indices:
        :return:
        """


class IProcedureJointFactory(IService):

    @abstractmethod
    def create(self, inner_procedure, outer_procedure, **kwargs):
        """
        :param inner_procedure:
        :param outer_procedure:
        :param kwargs:
        :return:
        """
