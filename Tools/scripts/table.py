import sys
sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/McM/')
from rest import McM
import json

mcm = McM(dev=False)

out_file = open("output.txt","w")

out_file.write('| *Dataset name* | *Extension* | *Gen prepid* | *Gen status* | *Total Gen* | *Completed Gen* | *Mini prepid* | *Mini status* | *Total Mini* | *Completed Mini* | *Nano prepid* | *Nano status* | *Total Nano* | *Completed Nano* |' + '\n')

input_file = open("prepid.txt","r")
sample_list = input_file.read().splitlines()

print(sample_list)

for sample in sample_list:

  root_query = 'prepid=' + sample
  
  root_requests = mcm.get('requests', query=root_query)
  
  for root_request in root_requests:
  
    out_file.write('| ' + root_request['dataset_name'] + ' | ' + str(root_request['extension']) + ' | ' + root_request['prepid'] + ' | ' + root_request['status'] + ' | ' + str(round(root_request['total_events']*100,2)) + ' | ' + str(round(float(root_request['completed_events'])/float(root_request['total_events']*100),2)))
  
    full_chain = root_request['member_of_chain']
  
    chain_counter = 0
    previous_mini = ""
  
    for nchain in full_chain:
  
      chain = nchain.split("-")[1]
      steps = chain.split("_")
      minichain = steps[len(steps)-2]
      nanochain = steps[len(steps)-1]
  
      minichain = minichain.split("flow")[1]
      nanochain = nanochain.split("flow")[1]
  
      search_mini = 'dataset_name=' + root_request['dataset_name'] + '&member_of_campaign=' + minichain + '&extension=' + str(root_request['extension'])
      mini_requests = mcm.get('requests', query=search_mini)
  
      if mini_requests:
        for mini_request in mini_requests:
  
          if chain_counter == 0:
            out_file.write(' | ' + mini_request['prepid'] + ' | ' + root_request['status'] + ' | ' + str(round(mini_request['total_events']*100,2)) + ' | ' + str(round(float(mini_request['completed_events'])/float(mini_request['total_events'])*100,2)))
  
          if chain_counter != 0:
            if mini_request['prepid'] == previous_mini:
              out_file.write('| ^ | ^ | ^ | ^ | ^ | ^ | ^ | ^ | ^ | ^')
            else:
              out_file.write('| ^ | ^ | ^ | ^ | ^ | ^' + ' | ' + mini_request['prepid'] + ' | ' + root_request['status'] + ' | ' + str(round(mini_request['total_events']*100,2)) + ' | ' + str(round(float(mini_request['completed_events'])/float(mini_request['total_events'])*100,2)))
  
          previous_mini = mini_request['prepid']
      else:
        out_file.write('| ^ | ^ | ^ | ^ | ^ | ^ | ^ | ^ | ^')
  
      search_nano = 'dataset_name=' + root_request['dataset_name'] + '&member_of_campaign=' + nanochain + '&extension=' + str(root_request['extension'])
      nano_requests = mcm.get('requests', query=search_nano)
  
      if nano_requests:
        for nano_request in nano_requests:
  
          if chain_counter == 0:
            out_file.write(' | ' + nano_request['prepid'] + ' | ' + root_request['status'] + ' | ' +  str(round(mini_request['total_events']*100,2)) + ' | ' + str(round(float(nano_request['completed_events'])/float(nano_request['total_events'])*100,2)))
    
          if chain_counter != 0:
            if nano_request['prepid'] == previous_nano:
              out_file.write(' | ^ | ^ | ^ | ^ | ^')
            else:
              out_file.write(' | ' + nano_request['prepid'] + ' | ' + root_request['status'] + ' | ' +  str(round(mini_request['total_events']*100,2)) + ' | ' + str(round(float(nano_request['completed_events'])/float(nano_request['total_events'])*100,2)))
    
          previous_nano = nano_request['prepid']
      else:
        out_file.write(' | ^ | ^ | ^ | ^')
  
      out_file.write(' | \n')
  
      chain_counter = chain_counter + 1 

out_file.close()
