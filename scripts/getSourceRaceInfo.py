import json
import re
import os
import sys, getopt

REF_DIR="references"
CDIR="micro-benchmarks"
FDIR="micro-benchmarks-fortran"

def main(argv):
	# micro-bechmarks in C
	cfiles = [f for f in os.listdir(CDIR) if os.path.isfile(os.path.join(CDIR, f))]
	for f in cfiles:
		fullpath = os.path.join(CDIR, f)
		print("processing C:" + fullpath)
		genRaceInfoJsonFile(fullpath,os.path.join(REF_DIR, "C"))

	# micro-bechmarks in fortran
	ffiles = [f for f in os.listdir(FDIR) if os.path.isfile(os.path.join(FDIR, f))]
	for f in ffiles:
		fullpath = os.path.join(FDIR, f)
		print("processing Fortran:"+fullpath)
		genRaceInfoJsonFile(fullpath,os.path.join(REF_DIR, "Fortran"))


def genRaceInfoJsonFile(inputfile, outputdir):
	filename = os.path.basename(inputfile)
	outputfile=filename.rsplit('.')[0]+'.json'
	if not os.path.exists(outputdir):
		os.makedirs(outputdir)
	outputfile=outputdir+'/'+outputfile
	# print ('Input: ', inputfile, ' Output:', outputfile)
	file = open(inputfile,"r")
	haveRace = False
	if re.search("-yes",filename):
		haveRace = True
	Lines = file.readlines()
	jsAry = []
	content = [line.strip() for line in Lines]

#
#  case 1: search for exact pair following the syntax: name1[idx]@row:column v.s. name2[idx2]@row:column
#  Example: a[i+1]@64:10 vs. a[i]@64:5
#           b[i][j]@75:7 vs. b[i][j-1]@75:15
#           *counter@63:6 vs. *counter@63:6  
#

	for i in range(0,len(content)):
		x = re.search("(?:\*)*[a-zA-Z]\S*(?:\[.*\])*\@\d+\:\d+\s+.+\s+(?:\*)*[a-zA-Z]\S*(?:\[.*\])*\@\d+\:\d+",content[i],flags=re.IGNORECASE)
		if(x):
			js = {}
			match = x.group()
			js["microbenchmark"] = filename
			#print(match)
			pair = re.findall("(?:\*)*[a-zA-Z]\S*(?:\[.*\])*\@\d+\:\d+", match)
			#print(i,pair)
			p1 = pair[0]
			p2 = pair[1]
			i1 = res = re.split('\@|\:', p1)
			i2 = res = re.split('\@|\:', p2)
			#print("left", i1)
			#print("right", i2)
			js["write_dataname"] = i1[0]
			js["write_line"] = i1[1]
			js["write_column"] = i1[2]
			js["read_dataname"] = i2[0]
			js["read_line"] = i2[1]
			js["read_column"] = i2[2]
			jsAry.append(js)
#
#  case 2: use write set and read set
#  Example:   Write_set = {j@61:10, j@61:20}
#             Read_set = {j@62:20, j@62:12, j@61:14, j@61:20}
#
	rset = {}
	wset = {}
	for i in range(0,len(content)):
		x = re.search("write_set\s*=\s*\{.*\}",content[i],flags=re.IGNORECASE)
		if(x):
			match = x.group()
			wset = re.findall("(?:\*)*[a-zA-Z]\S*(?:\[.*\])*\@\d+\:\d+", match)
			#print("wset has ", len(wset))
		
	for i in range(0,len(content)):
		x = re.search("read_set\s*=\s*\{.*\}",content[i],flags=re.IGNORECASE)
		if(x):
			match = x.group()
			rset = re.findall("(?:\*)*[a-zA-Z]\S*(?:\[.*\])*\@\d+\:\d+", match)
			#print("rset has ", len(rset))
	
	for r in rset:
		for w in wset:
			js = {}
			rinfo = res = re.split('\@|\:', r)
			winfo = res = re.split('\@|\:', w)
			js["microbenchmark"] = filename
			js["write_dataname"] = winfo[0]
			js["write_line"] = winfo[1]
			js["write_column"] = winfo[2]
			js["read_dataname"] = rinfo[0]
			js["read_line"] = rinfo[1]
			js["read_column"] = rinfo[2]
			jsAry.append(js)

	
	if (haveRace and len(jsAry) == 0):
		print(filename + " should have race but found no race encoding in source code!")
	elif ((not haveRace) and len(jsAry) != 0):
		print(filename + " should have no race but found race encoding in source code!")
	js = {}
	for i in range(len(jsAry)):
		js[i] = jsAry[i]
	
	with open(outputfile, 'w') as f:
		json.dump(js, f)

if __name__ == "__main__":
	main(sys.argv[1:])


