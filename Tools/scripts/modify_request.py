import sys
import os
import argparse
sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/McM/')
from rest import McM

parser = argparse.ArgumentParser()
parser.add_argument('--prepid', type=str, help="prepid(s) to search", nargs='+')
parser.add_argument('--notDev', help="Do not run in dev mode, actually do cloning", action='store_true')
parser.add_argument('--field_to_update', help="field to update")
parser.add_argument('--value', help="field to update valu")
args = parser.parse_args()

prepidToSearch = args.prepid
if prepidToSearch == None:
  sys.exit()

field_to_update = args.field_to_update
value = args.value

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
    if request['approval'] == 'none':
      print ''
      print 'I will modify {0}'.format(request['prepid'])
      print 'Request {0} field {1} BEFORE update: {2}'.format(request['prepid'], field_to_update, request[field_to_update])

    # Modify what we want
    # time_event is a list for each sequence step
    #request[field_to_update] = [value]
    if field_to_update == 'interested_pwg':
      request[field_to_update] = [value]
    else if field_to_update == 'memory':
      request[field_to_update] = value

    # Push it back to McM
    update_response = mcm.update('requests', request)
    #print('Update response: %s' % (update_response))

    # Fetch the request again, after the update, to check whether value actually changed
    request2 = mcm.get('requests', request['prepid'])
    print 'Request {0} field {1} BEFORE update: {2}'.format(request2['prepid'], field_to_update, request2[field_to_update])
