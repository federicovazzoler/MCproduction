import sys
import os
import argparse
sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/McM/')
from rest import McM

parser = argparse.ArgumentParser()
parser.add_argument('--desiredCampaign', type=str, help="Campaign in which you want to clone")
parser.add_argument('--prepid', type=str, help="List of prepids to clone", nargs='+')
parser.add_argument('--notDev', help="Do not run in dev mode, actually do cloning", action='store_true')
args = parser.parse_args()

PrepidsToClone = args.prepid
if PrepidsToClone == None:
	print 'Please provide list of prepids to clone'
	print 'e.g. python cloneFromTo.py --prepid TOP-RunIIFall18wmLHEGS-00XYZ TOP-RunIIFall18wmLHEGS-00ZYX'
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

def cloneTo(prepidToClone, desiredCampaign):
        campaign = desiredCampaign
	tag = ['EGM POG related studies']

	# Check dataset name doesn't already exist in this campaign
	otherRequests = mcm.get('requests', query='dataset_name={dataset}&member_of_campaign={campaign}'.format(dataset = prepidToClone['dataset_name'], campaign = campaign), method='get')
	if otherRequests != None:
		print '='*100
		print 'Dataset already exists in campaign, not going to clone'
		print 'Dataset to clone : ',prepidToClone['prepid'],prepidToClone['dataset_name']
		print 'Prepids already exisiting for this dataset:'
		for otherRequest in otherRequests:
			print otherRequest['prepid']
		print '='*100
		return None

	modifiedPrepid = prepidToClone
	modifiedPrepid['pwg'] = 'EGM'
	modifiedPrepid['interested_pwg'] = ['EGM']
	modifiedPrepid['member_of_campaign'] = campaign
	modifiedPrepid['ppd_tags'] = tag

	cloned_prepid = mcm.clone_request( modifiedPrepid )
	print 'Will clone to',campaign,'with tag',tag,'and prepid',cloned_prepid['prepid']
	return mcm.get('requests', cloned_prepid['prepid'], method='get')



for PrepidToClone in PrepidsToClone:
	print '\n---> Cloning',PrepidToClone
#	if not ( 'TOP-RunIIFall18wmLHEGS' in PrepidToClone ):
#		print 'This does not look like a Fall18 prepid, skipping :',PrepidToClone
#		continue

	# Get prepid from McM, check it exists
	PrepidFromMcM = mcm.get('requests', PrepidToClone, method='get')
	if len( PrepidFromMcM ) == 0:
		print 'This prepid does not exist in McM :',PrepidFromMcM
		print 'EXITING'
		sys.exit()

        #let's clone
	desiredCampaignPrepid = cloneTo(prepidToClone = PrepidFromMcM, desiredCampaign = args.desiredCampaign)
