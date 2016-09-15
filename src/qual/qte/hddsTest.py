import sys

from qual.pb2.HDDS_pb2 import HostDomainDeviceServiceRequest, HostDomainDeviceServiceResponse
from tklabs_utils.configurableObject.configurableObject import ConfigurableObject
from tklabs_utils.tzmq.ThalesZMQClient import ThalesZMQClient
from tklabs_utils.tzmq.ThalesZMQMessage import ThalesZMQMessage


## Class that provides a client to the HostDomainDeviceService function of QTA
class QTEHDDS(object):
    ## Constructor
    # @param server  Host name or IP address of QTA
    def __init__(self, server="localhost"):
        super(QTEHDDS, self).__init__()
        # Construct address to connect to
        address = str.format('tcp://{}:{}', server, 50001)
        ## Client connection to QTA
        self.client = ThalesZMQClient(address, timeout=7000)
        #print "Opened connection to", address, "for GPB messaging"

    ## Send request
    def sendRequest(self):
        hddsReq = HostDomainDeviceServiceRequest()
        if sys.argv[1].lower() == "get":
            hddsReq.requestType = HostDomainDeviceServiceRequest.GET
            for key in sys.argv[2:]:
                prop = hddsReq.values.add()
                prop.key = key
            response = self.client.sendRequest(ThalesZMQMessage(hddsReq))
            if response.name == "HostDomainDeviceServiceResponse":
                hddsResp = HostDomainDeviceServiceResponse()
                hddsResp.ParseFromString(response.serializedBody)
                for prop in hddsResp.values:
                    print("%s = '%s'%s" % (prop.key, prop.value, "" if prop.success else " <FAILURE>"))
        elif sys.argv[1].lower() == "set":
            hddsReq.requestType = HostDomainDeviceServiceRequest.SET
            for kv in sys.argv[2:]:
                splitkv = kv.split("=")
                if len(splitkv) != 2 or len(splitkv[0]) == 0:
                    continue
                prop = hddsReq.values.add()
                prop.key = splitkv[0]
                prop.value = splitkv[1]
            response = self.client.sendRequest(ThalesZMQMessage(hddsReq))
            if response.name == "HostDomainDeviceServiceResponse":
                hddsResp = HostDomainDeviceServiceResponse()
                hddsResp.ParseFromString(response.serializedBody)
                for prop in hddsResp.values:
                    print("%s = '%s'%s" % (prop.key, prop.value, "" if prop.success else " <FAILURE>"))
        else:
            print "Must specify GET or SET and at least one key (for GET) or key/value pair (for SET)"
            return 1

        return 0

## Main function for Qual HDDS test app
def main():
    if len(sys.argv) < 3:
        print "Must specify GET or SET and at least one key (for GET) or key/value pair (for SET)"
        return 1

    # Initialize and run the QTA client
    ConfigurableObject.setFilename("qual")
    qtehdds = QTEHDDS()
    # Call handler and return exit code for wrapper script
    return qtehdds.sendRequest()


if __name__ == "__main__":
    main()
