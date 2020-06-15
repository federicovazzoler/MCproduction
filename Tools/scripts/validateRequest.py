import sys
import os
import argparse
sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/McM/')
from rest import McM

parser = argparse.ArgumentParser()
parser.add_argument('--prepid', type=str, help="prepid(s) to search", nargs='+')
parser.add_argument('--notDev', help="Do not run in dev mode, actually do cloning", action='store_true')
args = parser.parse_args()

prepidToSearch = args.prepid
if prepidToSearch == None:
  sys.exit()

# Double check if it's ok to run not in dev mode
devMode = not args.notDev
if not devMode:
        answer = None
        while answer not in ["y", "n"]:
                answer = raw_input("Not in dev mode, ok to continue [Y/N]? ").lower()
        if not answer == 'y':
                sys.exit()

os.system('source /afs/cern.ch/cms/PPD/PdmV/tools/McM/getCookie.sh')
os.system('cern-get-sso-cookie -u https://cms-pdmv.cern.ch/mcm/ -o ~/private/prod-cookie.txt --krb --reprocess')
mcm = McM(dev=devMode)

for req_prepid in prepidToSearch:
  request = mcm.get('requests', query='prepid={0}'.format(req_prepid), method='get')
  if len(request) == 1:
    request = request[0]
    if request['approval'] == 'none' or (request['approval'] == 'validation' and request['status'] == 'validation'):
      print ''
      print 'I will trigger validation of {0}'.format(request['prepid'])
      print '-- request : ',request['dataset_name']
      print '-- link    : https://cms-pdmv.cern.ch/mcm/requests?prepid={0}'.format(request['prepid'])
      mcm.approve('requests', request['prepid'])
      print ''
    else:
      print ''
      print '[INFO] : Request {0} is in {1}'.format(request['prepid'], request['approval'])
      print '!!!'
      print ''
  else:
    print ''
    print '[ERROR] : Request {0} does not exists!'.format(req_prepid)
    print ''
