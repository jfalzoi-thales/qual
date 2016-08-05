import httplib

from common.configurableObject.configurableObject import ConfigurableObject


'''


'''
class VideoEncoder(ConfigurableObject):
    ## Constructor
    #  @param     self
    #  @param     config Configuration section lable (INI Section name)
    def __init__(self, config):
        super(VideoEncoder, self).__init__(config)

        self.configIP = '192.168.0.65'
        self.configPath = '/cgi-bin/config.cgi'
        self.broadcastIP = '192.168.0.65'
        self.broadcastPort = '52123'
        self.loadConfig(attributes=('configIP', 'configPath', 'broadcastIP','broadcastPort'))


    def formatPostData(self) :

        postDataShort = {
            'ip' : self.broadcastIP,
            'port': str(self.broadcastPort),
        }

        postDataFull = {
            'ip' : self.broadcastIP,
            'port': str(self.broadcastPort),
            'vidin' : 'COMPOSITE_A',
            'interface' : 'ETH',
            'audio_input' : 'Analog',
            'transport' : 'TS',
            'ac' : 'mp2',
            'audbitrate' : '128k',
            'encportpath' : '52123',
            'res' : 'FollowInput',
            'asibitrate' : '12000k',
            'ratecontrol' : 'CBR',
            'asipcrinterval' : '',
            'vidbitrate' : '2000k',
            'tspid' : '',
            'enc_vd' : '0',
            'enc_ad' : '0',
            'profile' : 'main',
            'gop' : '15',
            'local_ip' : '192.168.0.65',
            'maxdelay' : '300',
            'local_netmask' : '255.255.0.0',
            'vc' : 'h264',
            'default_gw' : '192.168.0.1',
            'fdiv' : '1',
            'videocrop' : '',
            'sharpness' : '0',
            'action' : 'SaveUser',
            'set_password' : '',
            'set_devicename' : '',
            'use_dhcp' : 'N',
            'opmode' : 'encoder',
            'encpath' : '/live/test',
            'devicename' : 'DME-01',
        }


        postData = postDataFull
        content = '\r\n'.join("%s=%s" % item for item in postData.iteritems())
        postData = 'Content-Type: text/plain\r\nContent-Length: %d\r\n\r\n%s' % (len(content), content)
        return postData

    def sendConfig(self):
        headers = {}
        headers['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0"
        headers['Accept-Language'] = "en-US,en;q=0.5"
        #headers['Accept-Encoding'] = "gzip, deflate"
        headers['Accept'] = 'application/json'
        conn = httplib.HTTPConnection(self.configIP, port=80)

        conn.connect()
        conn.request('POST', self.configPath,
                     body=self.formatPostData(), headers=headers)

        resp = conn.getresponse()
        rawResponse = resp.read()
        conn.close()

        return resp.status, rawResponse










            





