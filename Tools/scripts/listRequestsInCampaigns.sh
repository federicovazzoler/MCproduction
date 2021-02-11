#!/bin/bash

usage() { 
  echo "Usage: $0 [-h display help] [-c campaign] [-v verbose <true|false>]" 1>&2
  exit 1 
}

while getopts ":hc:v:" o; do
  case "${o}" in
    h)
      echo "Available campaigns:"
      echo ""
      echo "RunIISummer19UL16wmLHEGENAPV"
      echo "RunIISummer19UL16wmLHEGEN"
      echo "RunIISummer19UL16GENAPV"
      echo "RunIISummer19UL16GEN"
      echo "RunIISummer19UL17wmLHEGEN"
      echo "RunIISummer19UL17GEN"
      echo "RunIISummer19UL18wmLHEGEN"
      echo "RunIISummer19UL18GEN"
      echo "RunIISummer20UL16wmLHEGENAPV"
      echo "RunIISummer20UL16wmLHEGEN"
      echo "RunIISummer20UL17wmLHEGEN"
      echo "RunIISummer20UL18wmLHEGEN"
      echo "RunIISummer20UL16GENAPV"
      echo "RunIISummer20UL16GEN"
      echo "RunIISummer20UL17GEN"
      echo "RunIISummer20UL18GEN"
      echo "Run3Summer19GS"
      echo "Run3Summer19wmLHEGS"
      echo "Run3Winter20GS"
      echo "Run3Winter20wmLHEGS"
      echo ""
      exit 0
      ;;
    c)
      c=${OPTARG}
      ;;
    v)
      v=${OPTARG}
      ;;
    *)
      usage
      ;;
  esac
done
shift $((OPTIND-1))
if [ -z "${c}" ] || [ -z "${v}" ]; then
    usage
fi

python listRequests.py --notDev --verbose ${v} --campaigns ${c}

exit 0
