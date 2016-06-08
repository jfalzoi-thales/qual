

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
                typecast = lambda x: JsonConversion.pb2json(x)
            elif field.type == FD.TYPE_ENUM:
                typecast = lambda x: field.enum_type.values_by_number[int(x)].name
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

        return pbMessage.__class__.__name__, json

    @classmethod
    def json2pb(cls, pbMessage, json):

        #If the 1st param is a classname, convert it to a class
        if isinstance(pbMessage, str):
            pbMessage = JsonConversion.gpbClasses.getClassByName(pbMessage)

        for field in pbMessage.DESCRIPTOR.fields:
            if field.name not in json.keys():
                continue
            if field.type == FD.TYPE_MESSAGE:
                typecast =  lambda x: JsonConversion.json2pb(getattr(pbMessage, field.name), x)
                pass
            elif field.type == FD.TYPE_ENUM:
                typecast = lambda x: field.enum_type.values_by_name[unicode(x)].number
            elif field.type in JsonConversion.knownTypecasts:
                typecast = JsonConversion.knownTypecasts[field.type]
            else:
                raise Exception('%s.%s no typecast %d' % (pbMessage.__class__.__name__, field.name, field.type,))

            if field.label == FD.LABEL_REPEATED:
                valueList = getattr(pbMessage, field.name, [])
                for item in json[field.name] :
                    if field.type == FD.TYPE_MESSAGE:
                        JsonConversion.json2pb(valueList.add(), item)
                    else:
                        valueList.append(typecast(item))

            else:
                setattr(pbMessage, field.name, typecast(json[field.name]))
        return pbMessage

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

