## Classes to handle the exceptions ##

## Class for No method found
class MethodNotFoundException(Exception):
    def __init__(self, methodName):
        super(self).__init__()
        print 'Not method %s found' % (methodName,)


## Class for No method found
class WrongParamException(Exception):
    def __init__(self, expected, received ):
        super(self).__init__()
        print '%d parameters expected, but found %d instead' % (expected, received,)