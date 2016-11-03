import argparse
import json
from vtss import Vtss


# Parse command line arguments
params = argparse.ArgumentParser(description="Remote Procedure Calls.")
params.add_argument('-d',
                    dest='switch',
                    type=str,
                    default="192.168.1.1",
                    help="IP address of switch")
params.add_argument('-c',
                    dest='cmds',
                    nargs='+',
                    type=str,
                    help="Cmd to call with the RPC")
params.add_argument('-p',
                    dest='path',
                    type=str,
                    default="",
                    help="Path to place the spec file. If no path, the file will be downloaded to the same CWD")
params.add_argument('-r',
                    dest='results',
                    type=str,
                    default="results.json",
                    help="Path to place the result json. If no path, the file will be created in the same CWD")

args = params.parse_args()

# Call params
calls = []

# Vtss obj
obj = Vtss(args.switch, specDir=args.path)

if isinstance(args.cmds, str):
    calls.append(args.cmds)
else:
    calls = args.cmds

# execute the cmd
jsonData = obj.callMethod(calls)

# save the results
file = open(args.results, 'w+')
json.dump(jsonData, file, sort_keys=True, indent=4, ensure_ascii=False)
file.close()
