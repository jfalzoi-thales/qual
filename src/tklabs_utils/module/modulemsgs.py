
## Module Messages Base class
class ModuleMessages(object):

    ## Static method that returns menu title for use by a menu-driven QTE
    #
    # This must be implemented in each derived class
    #
    # @return Text to use for the name of the module these messages are associated with
    @staticmethod
    def getMenuTitle():
        return "Undefined"

    ## Static method that returns a menu for use by a menu-driven QTE
    #
    # This must be implemented in each derived class
    #
    # @return list of pairs of menu text and function to call that returns a message object
    @staticmethod
    def getMenuItems():
        return [("", None),]

    ## Constructor (not used)
    #  @param     self
    def __init__(self):
        return
