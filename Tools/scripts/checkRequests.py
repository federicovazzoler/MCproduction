import sys
import os
import argparse
sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/McM/')
from rest import McM

parser = argparse.ArgumentParser()
parser.add_argument('--campaigns', type=str, help="campaigns to search", nargs='+')
parser.add_argument('--notDev', help="Do not run in dev mode, actually do cloning", action='store_true')
args = parser.parse_args()

campaignsToSearch = args.campaigns
if campaignsToSearch == None:
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

for campaign in campaignsToSearch:
  print '*'*100
  print ''
  print 'Campaign : ', campaign
  print ''
  print '*'*100
  print ''
  foundRequests = mcm.get('requests', query='pwg=EGM&member_of_campaign={campaign}'.format(campaign = campaign), method='get')
  for foundRequest in foundRequests:
    print 'Request : ', foundRequest['dataset_name']
    print ' -- status             : ', foundRequest['status']
    print ' -- prepid             : ', foundRequest['prepid']
    print ' -- number of events   : ', foundRequest['total_events']
    #print ' -- completed events : ', foundRequest['completed_events']
    print ' -- member of chain(s)'
    for chain in range(0, len(foundRequest['member_of_chain'])):
      print ' ----> ', foundRequest['member_of_chain'][chain]
    print ''
