import scipy.io.numpyio as npio
import struct
import numpy as np


def parse(block):
    lastcount = -1
    index = 0
    blocklen = len(block)

    ret={}
    
    while(blocklen - index > 3):
        while ord(block[index]) & 0xF0 != 0x50:
	    index = index + 1
        scantype = ord(block[index]) & 0xF
        index = index+1
        counter = ord(block[index])
        if lastcount >= 0:
            if counter != lastcount+1 and not (lastcount == 255 and counter == 0):
                print "bad scan count: %d to %d" % (lastcount, counter)
        index = index+1
        scanlen = ord(block[index])
        if blocklen - index < scanlen:
            break

        if scanlen % 2 != 0 : print "odd scan length!"
	numscans = scanlen / 2

	datalists=[]
	if not ret.has_key(scantype):
		ret[scantype] = datalists
	else:
		datalists = ret[scantype]
	
	for i in range(numscans - len(datalists)):
		datalists.append([])

	for i in range(numscans):
		datalists[i].append(struct.unpack('<h', block[numscans:numscans+2]))
    return (ret, block[index:])

    
    
f=open('heli_data/capture', 'rb')


masterdata = {}
leftover = ""
r = f.read(8192)
while(len(r) > 0):
	(newdata, leftover) = parse(leftover + r)

	for key in newdata:
		if not masterdata.has_key(key):
			masterdata[key] = newdata[key]
		else:
			for key in newdata:
				masterdata[key] += newdata[key]
	r = f.read(8192)

for scantype in masterdata:
	masterdata[scantype] = np.array(masterdata[key])
	print masterdata[scantype].shape

#r=npio.fread(f, 1024, 'i')


