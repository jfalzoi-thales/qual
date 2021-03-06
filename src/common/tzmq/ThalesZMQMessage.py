
from common.gpb.python.MessageHeader_pb2 import MessageHeader


## Encapsulates a message as defined by the "Thales Common Network Messaging" document.
class ThalesZMQMessage(object):
    ## Constructor
    #
    # @param body Serializable object to use as message body
    # @param name Message name that identifies the type of this message
    #
    # There are two typical ways to construct a ThalesZMQMessage object.
    # Wrap a GPB message in a ThalesZMQMessage for outgoing use (most common);
    # this will auto-populate the name and header fields based on the body class:
    #    ThalesZMQMessage(responseBody)
    # Create a ThalesZMQMessage from incoming message data:
    #    request = ThalesZMQMessage(name=str(requestData[0])
    #    request.header.ParseFromString(requestData[1])
    #    request.serializedBody = requestData[2]
    #
    def __init__(self, body = None, name = ""):
        ## Message name that identifies the type of this message
        self.__name = name
        ## Message header in GPB object form
        self.__header = MessageHeader()
        ## Message body in GPB object form
        self.__body = None
        ## Message body in serialized form
        self.__serializedBody = None

        # Use setter to set the body to get auto-naming functionality
        self.body = body

    ## Get the message name that identifies the type of this message
    @property
    def name(self):
        return self.__name

    ## Set the message name that identifies the type of this message
    @name.setter
    def name(self, name):
        self.__name = name

    ## Get the message header in GPB object form
    @property
    def header(self):
        return self.__header

    ## Get the message header in serialized form
    @property
    def serializedHeader(self):
        return self.__header.SerializeToString()

    ## Get the message body in GPB object form
    @property
    def body(self):
        # Only one of body or serializedBody can be set, but unlike the serializedBody
        # property (see below), we can't automatically convert one to the other.
        # So just return body, meaning we could return None.
        return self.__body

    ## Set the message body in GPB object form
    @body.setter
    def body(self, body):
        # Only one of body or serializedBody can be set, so if we set one, we clear the other
        self.__body = body
        self.__serializedBody = None

        # Auto-update name based on class
        if self.__body is not None:
            self.__name = body.__class__.__name__
            self.__header.msg_name = self.__name

    ## Get the message body in serialized form
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

    ## Set the message body in serialized form
    @serializedBody.setter
    def serializedBody(self, serializedBody):
        # Only one of body or serializedBody can be set, so if we set one, we clear the other
        self.__serializedBody = serializedBody
        self.__body = None
