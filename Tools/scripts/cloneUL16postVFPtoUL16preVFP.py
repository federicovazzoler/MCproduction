import sys
import os
import argparse
sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/McM/')
from rest import McM

parser = argparse.ArgumentParser()
parser.add_argument('--prepid', type=str, help="List of UL16 prepids to clone", nargs='+')
parser.add_argument('--notDev', help="Do not run in dev mode, actually do cloning", action='store_true')
args = parser.parse_args()

UL16PrepidsToClone = args.prepid
if UL16PrepidsToClone == None or not all( ["RunIISummer19UL16GEN" in p or "RunIISummer19UL16wmLHEGEN" in p for p in UL16PrepidsToClone] ):
        print 'Please provide list of UL16 prepids to clone'
        print 'e.g. python cloneUL16ToUL.py --prepid TOP-RunIISummer19UL16wmLHEGEN-00XYZ TOP-RunIISummer19UL16wmLHEGEN-00ZYX'
        print 'or python cloneUL16ToUL.py --prepid TOP-RunIISummer19UL16GEN-00XYZ TOP-RunIISummer19UL16GEN-00ZYX'
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

def cloneToUL16PreVFP( prepidToClone ):

    campaign = 'RunIISummer19UL16wmLHEGENAPV' if "RunIISummer19UL16wmLHEGEN" in prepidToClone['prepid'] else 'RunIISummer19UL16GENAPV' 
    tag = [ 'ULPAG16' ]

    # Check dataset name doesn't already exist in this campaign
    otherRequests = mcm.get('requests', query='dataset_name={dataset}&member_of_campaign={campaign}'.format(dataset = prepidToClone['dataset_name'], campaign = campaign), method='get')
    if otherRequests != None:
        print '='*100
        print 'Dataset already exists in campaign, not going to clone'
        print 'UL16 prepid and dataset : ',prepidToClone['prepid'],prepidToClone['dataset_name']
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



for UL16PrepidName in UL16PrepidsToClone:
        print '\n---> Cloning',UL16PrepidName
        if not ( 'TOP-RunIISummer19UL16wmLHEGEN' in UL16PrepidName ):
                print 'This does not look like a UL16 prepid, skipping :',UL16PrepidName
                continue

        # Get prepid from McM, check it exists
        UL16PrepidFromMcM = mcm.get('requests', UL16PrepidName, method='get')
        if len( UL16PrepidFromMcM ) == 0:
                print 'This prepid does not exist in McM :',UL16PrepidFromMcM
                print 'EXITING'
                sys.exit()

        # Will clone to the 2016 UL campaign
        UL16APVPrepid = cloneToUL16PreVFP( prepidToClone = UL16PrepidFromMcM )
        if not UL16APVPrepid:
            print 'Dataset already existed in 2016 UL PreVFP campaign'
        else:
            print 'Cloned prepid to: %s'%UL16APVPrepid['prepid']
