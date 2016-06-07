

## Module Base class
class JsonConversion(object):


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




    @classmethod
    def encode(cls, message):
        messageName, fields = JsonConversion.loadMessage(message)


        return
'''
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