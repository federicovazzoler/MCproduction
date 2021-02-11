import sys
import os
import argparse
sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/McM/')
from rest import McM

def find_puScheme(chain):
  if chain == None:
    return None
 
  if 'Premix' in chain:
    return 'Premix'
  elif 'FlatPU0to70' in chain: 
    return 'Flat PU 0 To 70'
  elif 'FlatPU30to80' in chain:
    return 'Flat PU 30 To 80'
  elif 'FlatPU0to80' in chain:
    return 'Flat PU 0 To 80'
  else:
    return 'Classical'

def find_dataTier(chain):
  if chain == None:
    return None

  datatier = '' 
  if 'RAW' in chain: 
    datatier += ' RAW '
  if 'MiniAOD' in chain:
    datatier += ' MINIAOD '
  if 'NanoAOD' in chain: 
    datatier += ' NANOAOD '

  return datatier

def stripChain(chain):
  if chain == None:
    return None

  chain = chain[+4:]
  return chain[:-6]

def tinyURL(URL, prepid):
  if URL == None or prepid == None:
    return None
  
  return '[[{URL_string}][{text_string}]]'.format(URL_string = URL, text_string = prepid)

def colorStatus(status):
  if status == None:
    return None

  if status == 'done': return '%GREENBG% done %ENDBG%'
  elif status == 'submitted': return '%YELLOWBG% in production %ENDBG%'
  else: return '%REDBG% failed %ENDBG%'

parser = argparse.ArgumentParser()
parser.add_argument('--campaign', type=str, help="campaign to search")
args = parser.parse_args()

if args.campaign == None:
  sys.exit()

os.system('source /afs/cern.ch/cms/PPD/PdmV/tools/McM/getCookie.sh')
os.system('cern-get-sso-cookie -u https://cms-pdmv.cern.ch/mcm/ -o ~/private/prod-cookie.txt --krb --reprocess')
mcm = McM(dev=False)

output_file = open('TWIKI/{campaign}.txt'.format(campaign = args.campaign),'w')

#print table header
#output_file.write('---+++ Current EGM samples for {campaign} campaign\n'.format(campaign = args.campaign))
output_file.write('---+++ {campaign}\n'.format(campaign = args.campaign))
output_file.write('\n')
output_file.write('|  *Sample Name*  |  *status*  |  *Monitoring*  |  *Total Events* |  *pileup*  |  *GT*  |  *CMSSW release*  | *data tier*  |  *chain*  |\n')

#find request in campaign and print each entry
foundRequests = mcm.get('requests', query='pwg=EGM&member_of_campaign={campaign}'.format(campaign = args.campaign), method='get')
if foundRequests != None:
  for foundRequest in foundRequests:
    for chain in range(0, len(foundRequest['member_of_chain'])):
      output_file.write('|  {dataset_name}  |  {status}  |  {monitoring}  |  {tot_events} M  |  {pu_scheme}  |  {GT}  |  {cmssw_release}  | {datatier} |  {chain}  |\n'.format(dataset_name = foundRequest['dataset_name'], status = colorStatus(foundRequest['status']), monitoring = tinyURL('https://dmytro.web.cern.ch/dmytro/cmsprodmon/workflows.php?prep_id=task_{0}'.format(foundRequest['prepid']), foundRequest['prepid']), tot_events = float(foundRequest['total_events'])/1000000., pu_scheme = find_puScheme(foundRequest['member_of_chain'][chain]), GT = foundRequest['sequences'][0].get('conditions'), cmssw_release = foundRequest['cmssw_release'], datatier = find_dataTier(foundRequest['member_of_chain'][chain]), chain = stripChain(foundRequest['member_of_chain'][chain])))

output_file.write('\n')
output_file.close()
