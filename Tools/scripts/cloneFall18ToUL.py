import sys
import os
import argparse
sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/McM/')
from rest import McM

parser = argparse.ArgumentParser()
parser.add_argument('--prepid', type=str, help="List of Fall18 prepids to clone", nargs='+')
parser.add_argument('--notDev', help="Do not run in dev mode, actually do cloning", action='store_true')
args = parser.parse_args()

Fall18PrepidsToClone = args.prepid
if Fall18PrepidsToClone == None:
	print 'Please provide list of Fall18 prepids to clone'
	print 'e.g. python cloneFall18ToUL.py --prepid TOP-RunIIFall18wmLHEGS-00XYZ TOP-RunIIFall18wmLHEGS-00ZYX'
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

def cloneToUL( prepidToClone, yearToCloneInto ):
	campaign = 'RunIISummer19UL{year}wmLHEGS'.format( year = yearToCloneInto )
	tag = [ 'ULPAG{year}'.format( year = yearToCloneInto ) ]

	# Check dataset name doesn't already exist in this campaign
	otherRequests = mcm.get('requests', query='dataset_name={dataset}&member_of_campaign={campaign}'.format(dataset = prepidToClone['dataset_name'], campaign = campaign), method='get')
	if otherRequests != None:
		print '='*100
		print 'Dataset already exists in campaign, not going to clone'
		print 'Fall18 prepid and dataset : ',prepidToClone['prepid'],prepidToClone['dataset_name']
		print 'Prepids already exisiting for this dataset:'
		for otherRequest in otherRequests:
			print otherRequest['prepid']
		print '='*100
		return None

	modifiedPrepid = prepidToClone
	modifiedPrepid['interested_pwg'] = ['TOP']
	modifiedPrepid['member_of_campaign'] = campaign
	modifiedPrepid['ppd_tags'] = tag

	print 'Will clone to ',campaign,'with tag',tag
	cloned_prepid = mcm.clone_request( modifiedPrepid )
	return mcm.get('requests', cloned_prepid['prepid'], method='get')



for Fall18PrepidName in Fall18PrepidsToClone:
	print '\n---> Cloning',Fall18PrepidName
	if not ( 'TOP-RunIIFall18wmLHEGS' in Fall18PrepidName ):
		print 'This does not look like a Fall18 prepid, skipping :',Fall18PrepidName
		continue

	# Get prepid from McM, check it exists
	Fall18PrepidFromMcM = mcm.get('requests', Fall18PrepidName, method='get')
	if len( Fall18PrepidFromMcM ) == 0:
		print 'This prepid does not exist in McM :',Fall18PrepidFromMcM
		print 'EXITING'
		sys.exit()

	# Will clone to the 2018 UL campaign first
	# And then clone the new 2018 prepid to the 2017 and 2016 UL campaign
	UL18Prepid = cloneToUL( prepidToClone = Fall18PrepidFromMcM, yearToCloneInto = '18' )

	if UL18Prepid == None:
		print 'Dataset already existed in 2018 UL campaign, so not cloning to 2016 and 2017 campaigns'
	else:
		# Now clone to 2016 and 2017 UL campaign
		cloneToUL( prepidToClone = UL18Prepid, yearToCloneInto = '17' )
		cloneToUL( prepidToClone = UL18Prepid, yearToCloneInto = '16' )

