import os
import json
import httplib
import base64
from exception_Vtss import MethodNotFoundException, WrongParamException

## Class to handle wrap the VTSS switch interface
class Vtss(object):
    ## Constructor
    #
    #  @param: self
    #  @type:  str
    #  @param: switchIP - IP of the switch
    def __init__(self, switchIP=None, user='admin', password='', specFile='vtss-spec-rpc.spec'):
        #  IP of the switch
        self.ip = switchIP
        #  User name
        self.user = user
        #  Password
        self.password = password
        #  Spec file
        self.specFile = specFile

    ## Function to download the spec file from the switch
    #
    #  @type:  str
    #  @param: path - path to save the spec file. If not passed, 'cwd' will be used
    def downloadSpecFiles(self, path="", update=False):
        if path != "":
            #  Check if valid path
            if not os.path.exists(path):
                raise IOError
            self.specFile = '%s/%s' % (path, self.specFile)

        if not os.path.exists(self.specFile) or update:
            #  Init the connection
            http = httplib.HTTPConnection(self.ip, 80)

            ## Get the json specs
            auth = base64.b64encode(bytes('%s:%s' % (self.user, self.password,)).decode('utf-8'))
            header = {'Authorization': 'Basic %s' % auth}
            http.request('GET', '/json_spec', headers=header)
            resp = http.getresponse()

            #  Get the json in a string representation
            data = resp.read()

            #  Parse the json str
            jsonData = json.loads(data)

            # Create the spec file and write the content
            file = open(self.specFile, 'w+')
            json.dump(jsonData, file, sort_keys=True, indent=4, ensure_ascii=False)
            file.close()

    ## Function to execute a command in the switch
    #
    #  @type:  list<str>
    #  @param: request
    def callMethod(self, request=None):
        #  If the param is not a list, raise an exception
        if not isinstance(request, list):
            raise TypeError
        # get the json object
        jsonObj = self.getSpecs()

        #  Get the method dictonary in the json
        dic = None
        for method in jsonObj['methods']:
            if method['method-name'] == request[0]:
                dic = method
                break
        if dic == None:
            raise MethodNotFoundException(request[0])

        types = {}
        for type in jsonObj['types']:
            types[type['type-name']] = type

        params = []
        #  Check the params of the call and
        #  if the call has attributes
        if len(request) > 1:
            if len(request[1:]) != len(dic['params']):
                raise WrongParamException(len(dic['params'], len(request[1:])))

            i = 1
            for param in dic['params']:
                aux = self.parse_arg(types[param['type']], request[i])
                params.append(aux)
                i += 1
        aux = {"method": request[0], "params": params, "id": "jsonrpc"}

        #  make the post request to the switch
        post_body = json.dumps(aux)
        return self.postRequest(post_body)

    ## Function to get the json object of the spec file
    #
    #   @param: self
    #
    #   @note: If not spec file, then it downloads it
    def getSpecs(self):
        if not os.path.exists(self.specFile):
            self.downloadSpecFiles()
        file = open(self.specFile)
        content = file.read()
        return json.loads(content)

    ## This function return the representation in the spec file of any value
    #
    #  @param: type
    #  @param: val
    def parse_arg(self, type, val):
        encode = None

        if type.has_key('encoding-type'):
            encode = type['encoding-type']
        if type.has_key("json-encoding-type"):
            encode = type["json-encoding-type"]

        if encode == None:
            raise TypeError

        if encode == "String":
            return str(val)
        elif encode == "Number":
            return int(val)
        elif encode == "Boolean":
            if val in ['true', 'True']:
                return True
            elif val in ["false", 'False']:
                return False
            else:
                raise TypeError
        else:
            return json.loads(val)


    ## This function make the post request to the switch
    #
    #  @param: post
    def postRequest(self, post):
        #  Init the connection
        http = httplib.HTTPConnection(self.ip, 80)
        ## Get the json specs
        auth = base64.b64encode(bytes('%s:%s' % (self.user, self.password,)).decode('utf-8'))
        header = {'Authorization': 'Basic %s' % auth, 'Content-type': 'application/json'}
        http.request('POST',url='/json_rpc', body=post, headers=header)
        resp = http.getresponse()
        rawResponse = resp.read()

        return json.loads(rawResponse)