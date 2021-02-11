import sys
import os
import argparse
sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/McM/')
from rest import McM

parser = argparse.ArgumentParser()
parser.add_argument('--campaigns', type=str, help="campaigns to search", nargs='+')
parser.add_argument('--notDev', help="Do not run in dev mode", action='store_true')
parser.add_argument('--verbose', type=str, help="verbosity")
args = parser.parse_args()

campaignsToSearch = args.campaigns
if campaignsToSearch == None:
        sys.exit()

# Double check if it's ok to run not in dev mode
devMode = not args.notDev
if not devMode:
        #answer = None
        answer = 'y'
        while answer not in ["y", "n"]:
                answer = raw_input("Not in dev mode, ok to continue [Y/N]? ").lower()
        if not answer == 'y':
                sys.exit()

os.system('source /afs/cern.ch/cms/PPD/PdmV/tools/McM/getCookie.sh')
os.system('cern-get-sso-cookie -u https://cms-pdmv.cern.ch/mcm/ -o ~/private/prod-cookie.txt --krb --reprocess')
mcm = McM(dev=devMode)

for campaign in campaignsToSearch:
  print ''
  print ''
  print '*'*(15 + len(campaign))
  print '* CAMPAIGN :',campaign,'*'
  print '*'*(15 + len(campaign))
  print ''
  print ''
  foundRequests = mcm.get('requests', query='pwg=EGM&member_of_campaign={campaign}'.format(campaign = campaign), method='get')
  if foundRequests != None:
    nReq = 0
    nReqNew = 0
    nReqInValidation = 0
    nReqValid = 0
    nReqDefined = 0
    nReqSubmitted = 0
    nReqDone = 0
    reqToValidate_list = []
    reqToApprove_list = []

#    if args.table == 'true': 
#      outputFile = open('EGM_requests_' + campaign + '.txt','w')
#      outputFile.write('---+++++ Current EGM samples for ' + campaign + ' campaign\n')
#      outputFile.write('|  *Sample Name*  |  *status*  |  *Total Events* |  *pileup*  |  *GT*  | *data tier*  |  *purpose*  |  *chain*  |  *McM link*  |\n')

    for foundRequest in foundRequests:
      if args.verbose == 'true':
        print 'Request : ',foundRequest['dataset_name']
        print '-'*(11 + len(foundRequest['dataset_name']))
        print ''
        if foundRequest['approval'] == 'none': 
          print '!!! FAILED !!!'
          print ''
          reqToValidate_list.append(foundRequest['prepid'])
        if foundRequest['approval'] == 'validation' and foundRequest['status'] == 'validation': 
          reqToApprove_list.append(foundRequest['prepid'])
#        print ' -- link                   : https://cms-pdmv.cern.ch/mcm/requests?prepid={0}'.format(foundRequest['prepid']) 
        print ' -- link                   : https://dmytro.web.cern.ch/dmytro/cmsprodmon/workflows.php?prep_id=task_{0}'.format(foundRequest['prepid']) 
        print ' -- status                 :',foundRequest['status']
        print ' -- tags                   :',foundRequest['tags']
        print ' -- approval               :',foundRequest['approval']
        print ' -- prepid                 :',foundRequest['prepid']
        print ' -- number of events       :',float(foundRequest['total_events'])/1000000.,'M'
        print ' -- completed events (LHE) :', foundRequest['completed_events']
        print ' -- member of chain(s)'
        for chain in range(0, len(foundRequest['member_of_chain'])):
          print ' ---->',foundRequest['member_of_chain'][chain]
        print ''
        print ''
      nReq += 1
      if foundRequest['status'] == 'new': nReqNew += 1
      if foundRequest['status'] == 'new' and foundRequest['approval'] == 'validation': nReqInValidation += 1
      if foundRequest['status'] == 'validation': nReqValid += 1
      if foundRequest['status'] == 'defined': nReqDefined += 1
      if foundRequest['status'] == 'submitted': nReqSubmitted += 1
      if foundRequest['status'] == 'done': nReqDone += 1
    
#      if args.table == 'true': 
#        pileupString = ''
#        datatierString = ''
#        purpouseString = ''
#        chainString = ''
#        
#        outputFile.write('|  {0}  |  {1}  |  {2}  |  {3}  |  {4}  |  {5}  |  {6}  |  {7}  |  {8}  |\n'.format(foundRequest['dataset_name'], foundRequest['status'], float(foundRequest['total_events'])/1000000. + 'M', pileupString, foundRequest['GT'], datatierString, purpouseString, chainString, 'https://cms-pdmv.cern.ch/mcm/requests?prepid={0}'.format(foundRequest['prepid'])))
      
  print '-'*26
  print '# Request        :',nReq
  print '-- new           :',nReqNew
  print '-- in validation :',nReqInValidation
  print '-- valid         :',nReqValid
  print '-- defined       :',nReqDefined
  print '-- submitted     :',nReqSubmitted
  print '-- done          :',nReqDone
  print '-'*26
  if args.verbose == 'true':
    print ''
    print 'prepid to validate'
    print ''
    print 'python validateRequest.py --notDev --prepid',
    for prepid in range(len(reqToValidate_list)): 
      print reqToValidate_list[prepid],
    print ''
    print ''
    print 'prepid to approve'
    print ''
    print 'python validateRequest.py --notDev --prepid',
    for prepid in range(len(reqToApprove_list)): 
      print reqToApprove_list[prepid],
