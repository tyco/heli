import wx
import numpy as np

#ETSConfig.enable_toolkit = 'qt4'
from display import HeliDisplay, HeliPlotter

shortdtype = np.dtype('int16')

def parse(data, block, scancount):
    index = 0
    skipped = 0
    blocklen = len(block)
    
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
        if scanlen % 2 != 0: print "odd scan length!"
        num_chs = scanlen / 2
        # create a np array directly from this scan
        new_scan = np.ndarray(shape=(1,num_chs), dtype=np.int16, buffer=block[index:index+scanlen])
        index += scanlen
        
        if data.has_key(scantype):
            # append this scan as a row in the data matrix
            data[scantype] = np.vstack((data[scantype], new_scan))
        else:
            data[scantype] = new_scan
    
    return (block[index:], scancount)

# 10 scans at 10 Hz = 100 Hz
block_size = 10*25

def generate_data():    
    masterdata = {}
    f=open('../heli_data/imu_capture.1', 'rb')
    while(True):
        leftover = ""
        scancount = -1
        r = f.read(block_size)
        while(len(r) > 0):
            (leftover, scancount) = parse(masterdata, leftover + r, scancount)
            yield masterdata
            masterdata = {}
            r = f.read(block_size)
        f.seek(0)

    
class HeliApp(wx.PySimpleApp):
   
    def OnInit(self, *args, **kw):
        self.viewer = HeliDisplay()
        self.controller = HeliPlotter(viewer = self.viewer)
       
        # Pop up the windows for the two objects
        self.viewer.edit_traits()
        self.controller.edit_traits()
       
        self.generator = generate_data()
        
        # Set up the timer and start it up
        self.setup_timer(self.controller)
        return True
    
    def setup_timer(self, controller):    
        # Create a new WX timer
        timerId = wx.NewId()
        self.timer = wx.Timer(self, timerId)
       
        # Register a callback with the timer event
        self.Bind(wx.EVT_TIMER, self.timer_tick, id=timerId)
       
        # Start up the timer!  We have to tell it how many milliseconds
        # to wait between timer events.  For now we will hardcode it
        # to be 100 ms, so we get 10 updates per second.
        self.timer.Start(100.0, wx.TIMER_CONTINUOUS)
        return
    
    def timer_tick(self, *args):
        nextdata = self.generator.next()
        self.controller.plot_data(nextdata)

if __name__ == "__main__":
    app = HeliApp()
    app.MainLoop()
