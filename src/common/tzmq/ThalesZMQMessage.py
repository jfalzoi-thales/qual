
from common.gpb.python.MessageHeader_pb2 import MessageHeader


class ThalesZMQMessage(object):
    """
    Encapsulates a message as defined by the "Thales Common Network Messaging" document.
    """

    def __init__(self, name):
        """
        Constructor

        @param name Message name that identifies the type of this message
        """

        self.__name = name
        self.__header = MessageHeader()
        self.__header.msg_name = name
        self.__serializedBody = ""

    @property
    def name(self):
        return self.__name

    @property
    def header(self):
        return self.__header

    @property
    def serializedHeader(self):
        return self.__header.SerializeToString()

    @property
    def serializedBody(self):
        return self.__serializedBody

    @serializedBody.setter
    def serializedBody(self, serializedBody):
        self.__serializedBody = serializedBody
