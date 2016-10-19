from subprocess import call

from nms.host.pb2.nms_host_api_pb2 import UpgradeReq, UpgradeResp, I350, SWITCH
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage

## Upgrade Module
class Upgrade(Module):
    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def __init__(self, config = None):
        super(Upgrade, self).__init__(config)
        #  Adds handler to available message handlers
        self.addMsgHandler(UpgradeReq, self.handler)

    ## Handles incoming tzmq messages
    #  @param     self
    #  @param     msg   tzmq format message
    #  @return    ThalesZMQMessage object
    def handler(self, msg):
        response = UpgradeResp()

        if msg.body.target == I350:
            if msg.body.path.endswith(".txt"):
                self.upgradeI350EEPROM(response, msg.body.path)
            else:
                self.upgradeI350Flash(response, msg.body.path)
        elif msg.body.target == SWITCH:
            self.addResp(response, errCode=1003, errDesc="SWITCH specified as upgrade target")
        else:
            self.addResp(response, errCode=1002, errDesc="Unexpected Target %s" % msg.body.target)

        return ThalesZMQMessage(response)

    ## Adds another set of values to the repeated values response field
    #  @param   self
    #  @param   response    An UpgradeResp object
    #  @param   success     Success flag to be added to response, default False
    #  @param   errCode     Error code for optional ErrorMessage field
    #  @param   errDesc     Error description for optional ErrorMessage field
    def addResp(self, response, success=False, errCode=None, errDesc=""):
        response.success = success

        if errCode:
            response.error.error_code = errCode
            response.error.error_description = errDesc
            self.log.error(errDesc)

    ## Attempts to upgrade the I350 EEPROM using image specified
    #  @param   self
    #  @param   response    An UpgradeResp object
    #  @param   path        Path to upgrade image
    def upgradeI350EEPROM(self, response, path):
        if call(["eeupdate64e", "-nic=2", "-data", "%s" % path]) == 0:
            self.addResp(response, True)
        else:
            self.addResp(response, errCode=1002, errDesc="Unable to program I350 EEPROM.")

    ## Attempts to upgrade the I350 Flash using image specified
    #  @param   self
    #  @param   response    An UpgradeResp object
    #  @param   path        Path to upgrade image
    def upgradeI350Flash(self, response, path):
        if call(["i350-flashtool", "%s" % path]) == 0:
            self.addResp(response, True)
        else:
            self.addResp(response, errCode=1002, errDesc="Unable to program I350 flash.")
