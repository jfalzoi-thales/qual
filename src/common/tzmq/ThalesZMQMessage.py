
from common.gpb.python.MessageHeader_pb2 import MessageHeader


class ThalesZMQMessage(object):
    """
    Encapsulates a message as defined by the "Thales Common Network Messaging" document.
    """

    def __init__(self, name, body = None):
        """
        Constructor

        @param name Message name that identifies the type of this message
        """

        self.__name = name
        self.__header = MessageHeader()
        self.__header.msg_name = name
        self.__body = body
        self.__serializedBody = None

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
    def body(self):
        # Only one of body or serializedBody can be set, but unlike the serializedBody
        # property (see below), we can't automatically convert one to the other.
        # So just return body, meaning we could return None.
        return self.__body

    @body.setter
    def body(self, body):
        # Only one of body or serializedBody can be set, so if we set one, we clear the other
        self.__body = body
        self.__serializedBody = None

    @property
    def serializedBody(self):
        # Only one of body or serializedBody can be set.  If the (un-serialized) body is
        # set, assume it's a class we can serialize and try to serialize it.
        if self.__serializedBody is not None:
            return self.__serializedBody
        elif self.__body is not None:
            return self.__body.SerializeToString()
        else:
            return ""

    @serializedBody.setter
    def serializedBody(self, serializedBody):
        # Only one of body or serializedBody can be set, so if we set one, we clear the other
        self.__serializedBody = serializedBody
        self.__body = None
