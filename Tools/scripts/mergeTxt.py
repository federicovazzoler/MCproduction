import sys
import os

fileList = sys.argv[1].split(' ')
fileList.remove('')
fileList.insert(0, 'EGM_twiki_header')

with open('TWIKI/finalTable.txt', 'w') as outfile:
    for fname in fileList:
        with open('TWIKI/' + fname + '.txt') as infile:
            for line in infile:
                outfile.write(line)
