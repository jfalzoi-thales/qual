import socket
import time
import subprocess

from nms.host.pb2.nms_host_api_pb2 import HealthInfoReq, HealthInfoResp
from tklabs_utils.module.module import Module
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage
from tklabs_utils.vtss.vtss import Vtss


## HealthInfo Module Class
class HealthInfo(Module):
    ## Constructor
    #  @param       self
    #  @param       config - Configuration for the instance is going to be created
    def __init__(self, config=None):
        # Constructor of the parent class
        super(HealthInfo, self).__init__(config)
        ## Flag to determine the health state
        self._health = True
        ## Flag to determine the switch health state
        self._switchHealth = True
        ## i350 divice
        self.i350EthernetDev = 'ens1f'
        ## IP address of the switch
        self.switchAddress = "10.10.41.159"
        ## Switch user name
        self.switchUser = 'admin'
        ## IP address of the switch
        self.switchPassword = ''
        # Load config file
        self.loadConfig(attributes=('i350EthernetDev','switchAddress','switchUser','switchPassword',))
        self.i350EthernetDev += '0'
        # VTSS object to talk with the switch
        self.vtss = Vtss(self.switchAddress, self.switchUser, self.switchPassword)
        # Add the message handler
        self.addMsgHandler(HealthInfoReq, self.handleMsg)
        # Thread to monitor switch CPU loading
        self.addThread(self.switchCPULoading)
        # Now we can start our thread
        self.startThread()

    ## Handles incoming messages
    #
    #  Receives tzmq request and runs requested process
    #
    #  @param:    self
    #  @param     msg       TZMQ format message
    #  @return    a ThalesZMQMessage object containing the response message
    def handleMsg(self, msg):
        #  Create the response object
        response = HealthInfoResp()

        # One time loop
        while True:
            # Check for switch health
            if self._switchHealth:
                response.healthy = True
            else:
                response.healthy = False
                response.unhealthy_reason = 'Unable to communicate with the switch.'
                break
            # Check for i350 health
            if self._runEthtool():
                response.healthy = True
            else:
                response.healthy = False
                response.unhealthy_reason = 'Unable to communicate with the i350EthernetDevice.'
                break

            # Get out of the loop
            break

        return ThalesZMQMessage(response)

    ## runs ethtool
    #  @param   self
    #  @return  bool    True if can talk to the device, otherwise False
    def _runEthtool(self):
        try:
            subprocess.check_output(["ethtool", self.i350EthernetDev])
            return True
        except subprocess.CalledProcessError:
            return False

    ## Request the CPU loading from the switch
    #
    #  @param: self
    #  @note: this function will run in a separate thread
    def switchCPULoading(self):
        try:
            response = self.vtss.callMethod(['system-utility.status.cpu-load.get'])
            if response['error'] == None:
                self._switchHealth = True
                self.log.info('Switch CPU load (Average10sec): %d'%response['result']['Average10sec'])
            else:
                # we could talk to the switch, but there was an error and this is not good!!!
                self._switchHealth = False
        except socket.error:
            # We couldn't talk to the switch
            self._switchHealth =  False
        finally:
            # we'll wait 1 min to run the test again
            timeout = 120
            while (timeout>0):
                # If someone terminated the thread while we were running amixer, don't start playback
                if not self._running:
                    return
                time.sleep(0.5)
                timeout -= 1


    ## Stops background thread
    #  @param     self
    def terminate(self):
        if self._running:
            self._running = False
            self.stopThread()