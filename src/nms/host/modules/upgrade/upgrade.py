import socket
import shutil
import os

from subprocess import call
from time import sleep


from nms.host.pb2.nms_host_api_pb2 import UpgradeReq, UpgradeResp, I350, SWITCH, INVALID_NAME, VLAN_ASSIGNMENT_FAILED, ERROR_PROCESSING_MESSAGE, NETWORK_MANAGEMENT_SERVICE_ERROR,FAILED_OBTAINING_SWITCH_INFORMATION, FAILURE_TO_OBTAIN_INVENTORY,UPGRADE_FAILED, INVALID_UPGRADE_PACKAGE_PROVIDED
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from tklabs_utils.vtss.vtss import Vtss

## Upgrade Module
class Upgrade(Module):
    ## Constructor
    #  @param     self
    #  @param     config  Configuration for this module instance
    def __init__(self, config = None):
        super(Upgrade, self).__init__(config)
        # Switch IP address
        self.switchIP = '10.10.41.159'
        ## User name for switch
        self.switchUser = 'admin'
        ## Password for switch
        self.switchPassword = ''
        ## TFTP server path
        self.tftpServerPath = '/thales/qual/firmware/'
        # Load the configuration
        self.loadConfig(['switchAddress','switchUser','switchPassword','tftpServerPath'])
        # Adds handler to available message handlers
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
            if msg.body.path.endswith(".dat"):
                self.upgradeVitesseSwitch(response, msg.body.path)
            else:
                self.updateConfig(response, msg.body.path)
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
            self.log.info('I350EEPROM updated. File name: %s'%(os.path.basename(path)))
        else:
            self.addResp(response, errCode=1002, errDesc="Unable to program I350 EEPROM.")

    ## Attempts to upgrade the I350 Flash using image specified
    #  @param   self
    #  @param   response    An UpgradeResp object
    #  @param   path        Path to upgrade image
    def upgradeI350Flash(self, response, path):
        if call(["i350-flashtool", "%s" % path]) == 0:
            self.addResp(response, True)
            self.log.info('i350Flash updated. File name: %s'%(os.path.basename(path)))
        else:
            self.addResp(response, errCode=1002, errDesc="Unable to program I350 flash.")

    ## Attempts to update startup config
    #  @param   self
    #  @param   response    An UpgradeResp object
    #  @param   path        Path to startup-config file
    def updateConfig(self, response, path):
        # Copy the file into the tftp server directory
        try:
            shutil.copy(path, self.tftpServerPath)
            # Object to call switch functions
            vtss = Vtss(switchIP=self.switchIP)
            # Try to update the configuration
            response = vtss.callMethod(['icfg.control.copy.set',
                                        '{"Copy":true,"SourceConfigFile":"tftp://192.168.1.122/%s","SourceConfigType":"configFile","DestinationConfigType":"startupConfig"}'%(os.path.basename(path))])
            # Check the response
            if response['error']:
                # Something went wrong with the RPC!!!
                self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Unable to update configuration.")
                return
        except EnvironmentError:
            self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Unable to copy config file into the tftp server.")
        except Exception:
            self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Unable to update configuration.")
        else:
            # Here the switch accepted the command and it's trying to copy
            try:
                # We'll wait around 5 seconds
                waitTime = 5
                while waitTime >= 0:
                    # Wait 1 second
                    sleep(1)
                    # Call upgrade process status
                    response = vtss.callMethod(['icfg.status.copy.get'])
                    # If there is an error calling status, probably we have an error
                    if response['error']:
                        self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Unable to update configuration.")
                        return
                    # Check the status of the procedure
                    status = response['result']['Status']
                    # Posibles responses from the switch
                    # "none"
                    if status == 'none':
                        pass
                    # "success"
                    if status == 'success':
                        self.addResp(response, success=True)
                        self.log.info('Switch configuration updated. File name: %s'%(os.path.basename(path)))
                        return
                    # "inProgress"
                    elif status == 'inProgress':
                        pass
                    # "errOtherInProcessing"
                    elif status == 'errOtherInProcessing':
                        self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Other file in progress.")
                        return
                    # "errNoSuchFile"
                    elif status == 'errNoSuchFile':
                        self.addResp(response, errCode=INVALID_UPGRADE_PACKAGE_PROVIDED, errDesc="Error: No such a file.")
                        return
                    # "errSameSrcDst"
                    elif status == 'errSameSrcDst':
                        self.addResp(response, errCode=INVALID_UPGRADE_PACKAGE_PROVIDED, errDesc="Error: Same source and destination file.")
                        return
                    # "errPermissionDenied"
                    elif status == 'errPermissionDenied':
                        self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Permission denied.")
                        return
                    # "errLoadSrc"
                    elif status == 'errLoadSrc':
                        self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Loading source.")
                        return
                    # "errSaveDst"
                    elif status == 'errSaveDst':
                        self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Saving in destination.")
                        return
                # If we get out of the loop, the process probably failed
                self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Timeout.")
            except Exception:
                # But here something went wrong trying to call status method!!!
                self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Unable to upgrade switch.")

    ## Attempts to upgrade the Vitesse Switch
    #
    #  @param   self
    #  @param   response    An UpgradeResp object
    #  @param   path        Path to upgrade image
    def upgradeVitesseSwitch(self, response, path):
        # Copy the file into the tftp server directory
        try:
            shutil.copy(path, self.tftpServerPath)
            # Object to call switch functions
            vtss = Vtss(switchIP=self.switchIP)
            # Try to upgrade the switch
            response = vtss.callMethod(['firmware.control.image-upload.set','{"DoUpload":true,"Url":"tftp://192.168.1.122/%s","ImageType":"firmware"}'%(os.path.basename(path))])
            # Check the response
            if response['error']:
                # Something went wrong with the RPC!!!
                self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Unable to upgrade switch.")
                return
        except EnvironmentError:
            self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Unable to copy image into the tftp server.")
        except Exception:
            self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Unable to upgrade switch.")
        else:
            # Here the switch accepted the command and it's trying to upgrade the firmware
            try:
                # flag to to check if the copy process started
                copyStarted = False
                # We'll wait around 8 minutes for the upgrade process
                waitTime = 60*8
                while waitTime >= 0:
                    # Wait 1 second
                    sleep(1)
                    # Call upgrade process status
                    response = vtss.callMethod(['firmware.status.image-upload.get'])
                    # If there is an error calling status, probably we have an error
                    if response['error']:
                        self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Unable to upgrade switch.")
                        return
                    # Check the status of the procedure
                    status = response['result']['Status']
                    # Posibles responses from the switch
                    # "none"
                    if status == 'none':
                        pass
                    # "inProgress"
                    elif status == 'inProgress':
                        copyStarted = True
                    # "errIvalidIp"
                    elif status == 'errIvalidIp':
                        self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Invalid IP address.")
                        return
                    # "errTftpFailed"
                    elif status == 'errTftpFailed':
                        self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: tftp server failed.")
                        return
                    # "errBusy"
                    # The switch is doing something else and it can't perform the request
                    elif status == 'errBusy':
                        self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Device busy.")
                        return
                    # "errMemoryInsufficient"
                    elif status == 'errMemoryInsufficient':
                        self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Memory insufficient in the device.")
                        return
                    # "errInvalidImage"
                    elif status == 'errInvalidImage':
                        self.addResp(response, errCode=INVALID_UPGRADE_PACKAGE_PROVIDED, errDesc="Error: Invalid upgrade package provided.")
                        return
                    # "errWriteFlash"
                    elif status == 'errWriteFlash':
                        self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Unable to write file into the flash.")
                        return
                    # "errSameImageExisted"
                    elif status == 'errSameImageExisted':
                        self.addResp(response, success=True)
                        return
                    # "errUnknownImage"
                    elif status == 'errUnknownImage':
                        self.addResp(response, errCode=INVALID_UPGRADE_PACKAGE_PROVIDED, errDesc="Error: Unknown upgrade package provided.")
                        return
                    # "errFlashImageNotFound"
                    elif status == 'errFlashImageNotFound':
                        self.addResp(response, errCode=INVALID_NAME, errDesc="Error: Image not found.")
                        return
                    # "errFlashEntryNotFound"
                    elif status == 'errFlashEntryNotFound':
                        self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Flash entry not found.")
                        return
                    # "errCrc"
                    elif status == 'errCrc':
                        self.addResp(response, errCode=INVALID_UPGRADE_PACKAGE_PROVIDED, errDesc="Error: CRC.")
                        return
                    # "errImageSize"
                    elif status == 'errImageSize':
                        self.addResp(response, errCode=INVALID_UPGRADE_PACKAGE_PROVIDED, errDesc="Error: Invalid image size.")
                        return
                    # "errEraseFlash"
                    elif status == 'errEraseFlash':
                        self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Unable to erase the flash.")
                        return
                    # "errIncorrectImageVersion"
                    elif status == 'errIncorrectImageVersion':
                        self.addResp(response, errCode=INVALID_UPGRADE_PACKAGE_PROVIDED, errDesc="Error: Incorrect image version.")
                        return
                    # "errDownloadUrl"
                    elif status == 'errDownloadUrl':
                        self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Downloading image.")
                        return
                    # "errInvalidUrl"
                    elif status == 'errInvalidUrl':
                        self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Invalid URL.")
                        return

                # If we get out of the loop, the process failed
                self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Invalid URL.")
            except socket.error:
                if copyStarted:
                    # When we can't connect to the switch, and the copy process started it's probably because it restarted as part of the upgrade process
                    self.addResp(response,success=True)
                    self.log.info('Switch firmware upgraded. File name: %s'%(os.path.basename(path)))
                else:
                    # When we can't connect to the switch, and the copy process didn't started, we got an error
                    self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Invalid URL.")
            except Exception:
                # But here something went wrong trying to call status method!!!
                self.addResp(response, errCode=UPGRADE_FAILED, errDesc="Error: Unable to upgrade switch.")