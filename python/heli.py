import numpy as np

shortdtype = np.dtype('int16')

def parse(data, block, scancount):
    index = 0
    blocklen = len(block)
    print "blocklen: %d"  % blocklen
    
    skipped = 0
    
    while(blocklen - index > 3):
        typebyte = ord(block[index])
        if typebyte & 0xF0 != 0x50:
            index = index + 1
            skipped = skipped + 1            
            continue
        scantype = typebyte & 0xF
        index = index+1
        counter = ord(block[index])
        if scancount >= 0:
            if counter != scancount+1 and not (scancount == 255 and counter == 0):
                print "bad scan count: %d to %d" % (scancount, counter)
        index = index+1
        scanlen = ord(block[index])
        index = index+1
        if blocklen - index < scanlen:
            # back up to the start of the scan header
            index = index - 3
            break

        scancount = counter
        if scanlen % 2 != 0 : print "odd scan length!"
        num_chs = scanlen / 2
        if(num_chs != 11): print num_chs

        new_scan = np.ndarray(shape=(1,num_chs), dtype=np.int16, buffer=block[index:index+num_chs*2])
        index += num_chs*2
        
        if data.has_key(scantype):
            #print "new: %s, old: %s" % (str(new_scan.shape), str(data[scantype].shape))
            data[scantype] = np.vstack((data[scantype], new_scan))
        else:
            data[scantype] = new_scan
    
    return (block[index:], scancount)

    
import os
print os.curdir
f=open('../heli_data/imu_capture.1', 'rb')

masterdata = {}
leftover = ""
scancount = -1
r = f.read(8192)
while(len(r) > 0):
    (leftover, scancount) = parse(masterdata, leftover + r, scancount)
    print len(leftover)
    r = f.read(8192)

#r=npio.fread(f, 1024, 'i')

