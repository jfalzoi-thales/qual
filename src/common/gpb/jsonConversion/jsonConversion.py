

## Module Base class
from common.classFinder.classFinder import ClassFinder
from google.protobuf.message import Message
from google.protobuf.descriptor import FieldDescriptor as FD


class JsonConversion(object):

    ## All available classes in GPB modules for QTA,
    gpbClasses = ClassFinder(rootPath='common.gpb.python', baseClass=Message)


    @classmethod
    def pb2json(cls, pbMessage):

        fields = pbMessage.ListFields()
        json = {}

        for field, value in fields:
            if field.type == FD.TYPE_MESSAGE:
                # Need to handle a nested message
                typecast = JsonConversion.pb2json
                pass
            elif field.type == FD.TYPE_ENUM:
                typecast = lambda x: 'Boo.%d' % (x,)
            elif field.type in JsonConversion.knownTypecasts:
                typecast = JsonConversion.knownTypecasts[field.type]
            else:
                raise Exception('%s.%s no typecast %d' % (pbMessage.__class__.__name__, field.name, field.type,))

            #If the value is a list, need to create the json List and populate each one
            if field.label == FD.LABEL_REPEATED:
                json[field.name] = []
                for item in value:
                    json[field.name].append(typecast(item))
            else:
                json[field.name] = typecast(value)

        return json

    knownTypecasts = {
        FD.TYPE_DOUBLE: float,
        FD.TYPE_FLOAT: float,
        FD.TYPE_INT64: long,
        FD.TYPE_UINT64: long,
        FD.TYPE_INT32: int,
        FD.TYPE_FIXED64: float,
        FD.TYPE_FIXED32: float,
        FD.TYPE_BOOL: bool,
        FD.TYPE_STRING: unicode,
        FD.TYPE_BYTES: lambda x: x.encode('string_escape'),
        FD.TYPE_UINT32: int,
        FD.TYPE_ENUM: int,
        FD.TYPE_SFIXED32: float,
        FD.TYPE_SFIXED64: float,
        FD.TYPE_SINT32: int,
        FD.TYPE_SINT64: long,
    }

'''

    @classmethod
    def json2pb(cls, messageName, json):
        pbMessage = JsonConversion.gpbClasses.getClassByName(messageName)

        messageName, fields = JsonConversion.loadMessage(message)
        return messageName, fields


    @classmethod
    def loadMessage(cls, message):
        messageFields = {}
        for field in message.DESCRIPTOR.fields:
            messageFields[field.name] =  {
                    'default' : field.default_value,
                    'value': field.default_value
            }


        for field in message._fields.keys():
            if field.name in messageFields.keys():
                messageFields[field.name]['value'] = message._fields[field]


        return message.DESCRIPTOR.name, messageFields

    def test_CPULoading(self):
        message = CPULoadingRequest()
        newMessage = CPULoadingRequest()
        self.log.info("REPORT before CPU load:")
        message.requestType = CPULoadingRequest.REPORT

        for field in message.DESCRIPTOR.fields :
            print field.name

        myDict = {}
        for field in  message._fields.keys() :
            myDict[field.name] = message._fields[field]




        self.sendReqAndLogResp(ThalesZMQMessage(message))
        sleep(3)
'''