from common.classFinder.classFinder import ClassFinder
from google.protobuf.message import Message
from google.protobuf.descriptor import FieldDescriptor as FD

## A class that serializes /Deserializes GPB buffers to/from JSON.
#
# Example:
#  @code{.py}
#         message = CPULoadingRequest()
#         message.requestType = CPULoadingRequest.RUN
#         message.level = 50
#         messageName, json = JsonConversion.gpb2json(message)
#         newMessage = JsonConversion.json2gpb(messageName, json)
#         self.assertEqual(message.level, newMessage.level)
#         self.assertEqual(message.requestType, newMessage.requestType)
#  @endcode
class JsonConversion(object):

    ## All available classes in GPB modules for QTA,
    _knownGpbClasses = ClassFinder(rootPath='common.gpb.python', baseClass=Message)

    ##Convert a GPB buffer object into a JSON object
    #@param cls This is a class method
    #@param pbMessage A GPB message object
    #returns tuple, messagename, json message data
    @classmethod
    def gpb2json(cls, pbMessage):

        fields = pbMessage.ListFields()
        json = {}

        for field, value in fields:
            if field.type == FD.TYPE_MESSAGE:
                # Need to handle a nested message, only use the json return code (thus [1])
                typecast = lambda x: JsonConversion.gpb2json(x)[1]
            elif field.type == FD.TYPE_ENUM:
                typecast = lambda x: field.enum_type.values_by_number[int(x)].name
            elif field.type in JsonConversion._knownTypecasts:
                typecast = JsonConversion._knownTypecasts[field.type]
            else:
                raise Exception('%s.%s no typecast %d' % (pbMessage.__class__.__name__, field.name, field.type,))

            #If the value is a list, need to create the json List and populate each one
            if field.label == FD.LABEL_REPEATED:
                json[field.name] = []
                for item in value:
                    json[field.name].append(typecast(item))
            else:
                json[field.name] = typecast(value)

        return pbMessage.__class__.__name__, json

    ##Convert a JSON object into a GPB Buffer
    #@param cls This is a class method
    #@param pbMessage A GPB message object, or string name of GPB message
    #@param json JSON serialized message data
    #returns GPB message object
    @classmethod
    def json2gpb(cls, pbMessage, json):

        #If the 1st param is a classname, convert it to a class
        if isinstance(pbMessage, str):
            pbMessage = JsonConversion._knownGpbClasses.getClassByName(pbMessage)()

        for field in pbMessage.DESCRIPTOR.fields:
            if field.name not in json.keys():
                #need to set default values that were not in json
                if field.label != FD.LABEL_REPEATED :
                    if field.has_default_value :
                        setattr(pbMessage, field.name, field.default_value)
                continue

            if field.type == FD.TYPE_MESSAGE:
                typecast =  lambda x: JsonConversion.json2gpb(getattr(pbMessage, field.name), x)
                pass
            elif field.type == FD.TYPE_ENUM:
                typecast = lambda x: field.enum_type.values_by_name[unicode(x)].number
            elif field.type in JsonConversion._knownTypecasts:
                typecast = JsonConversion._knownTypecasts[field.type]
            else:
                raise Exception('%s.%s no typecast %d' % (pbMessage.__class__.__name__, field.name, field.type,))

            if field.label == FD.LABEL_REPEATED:
                valueList = getattr(pbMessage, field.name, [])
                for item in json[field.name] :
                    if field.type == FD.TYPE_MESSAGE:
                        JsonConversion.json2gpb(valueList.add(), item)
                    else:
                        valueList.append(typecast(item))

            else:
                typecastValue = typecast(json[field.name])
                if field.type == FD.TYPE_MESSAGE:
                    # If this assignment is to a composite field (like a sub-message) we will get
                    # an attribute error. so use CopyFrom for messages.
                    setField = getattr(pbMessage, field.name, None)
                    if setField is None:
                        raise Exception('%s field getAttr error' % (field.name))
                    setField.CopyFrom(typecastValue)
                else:
                    setattr(pbMessage, field.name, typecastValue)

        return pbMessage

    ##A quick table for easy value typecasting, lookup by GPB field type.
    _knownTypecasts = {
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

