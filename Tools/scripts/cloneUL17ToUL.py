import sys
import os
import argparse
sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/McM/')
from rest import McM

parser = argparse.ArgumentParser()
parser.add_argument('--prepid', type=str, help="List of UL17 prepids to clone", nargs='+')
parser.add_argument('--notDev', help="Do not run in dev mode, actually do cloning", action='store_true')
args = parser.parse_args()

UL17PrepidsToClone = args.prepid
if UL17PrepidsToClone == None:
        print 'Please provide list of UL17 prepids to clone'
        print 'e.g. python cloneUL17ToUL.py --prepid TOP-RunIISummer19UL17wmLHEGEN-00XYZ TOP-RunIISummer19UL17wmLHEGEN-00ZYX'
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
    if yearToCloneInto == "17":
        print 'Cannot clone UL17 to UL17'
        return None

    campaign = 'RunIISummer19UL{year}wmLHEGEN'.format( year = yearToCloneInto )
    tag = [ 'ULPAG{year}'.format( year = yearToCloneInto ) ]

    # Check dataset name doesn't already exist in this campaign
    otherRequests = mcm.get('requests', query='dataset_name={dataset}&member_of_campaign={campaign}'.format(dataset = prepidToClone['dataset_name'], campaign = campaign), method='get')
    if otherRequests != None:
        print '='*100
        print 'Dataset already exists in campaign, not going to clone'
        print 'UL17 prepid and dataset : ',prepidToClone['prepid'],prepidToClone['dataset_name']
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



for UL17PrepidName in UL17PrepidsToClone:
        print '\n---> Cloning',UL17PrepidName
        if not ( 'TOP-RunIISummer19UL17wmLHEGEN' in UL17PrepidName ):
                print 'This does not look like a UL17 prepid, skipping :',UL17PrepidName
                continue

        # Get prepid from McM, check it exists
        UL17PrepidFromMcM = mcm.get('requests', UL17PrepidName, method='get')
        if len( UL17PrepidFromMcM ) == 0:
                print 'This prepid does not exist in McM :',UL17PrepidFromMcM
                print 'EXITING'
                sys.exit()

        # Will clone to the 2018 UL campaign first
        # And then clone to the 2018 UL campaign
        UL18Prepid = cloneToUL( prepidToClone = UL17PrepidFromMcM, yearToCloneInto = '18' )
        if not UL18Prepid:
                print 'Dataset already existed in 2018 UL campaign'
#        else:
#            print UL18Prepid
        UL16Prepid = cloneToUL( prepidToClone = UL17PrepidFromMcM, yearToCloneInto = '16' )
        if not UL16Prepid:
                print 'Dataset already existed in 2016 UL campaign'
#        else:
#            print UL16Prepid
