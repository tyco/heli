'''
Created on Nov 3, 2010

@author: tyler
'''

import numpy as np
from enthought.traits.api import Array, Bool, Callable, Enum, Float, HasTraits, \
                                 Instance, Int, Trait
from enthought.traits.ui.api import Group, HGroup, Item, View, spring, Handler
from enthought.pyface.timer.api import Timer
from enthought.chaco.chaco_plot_editor import ChacoPlotItem

class HeliDisplay(HasTraits):
    
    """ 
    based on data_stream Chaco example. 
    This class just contains the two data arrays that will be updated
    by the Controller.  The visualization/editor for this class is a
    Chaco plot.
    """
   
    index = Array   
    data = Array
    
    plot_type = Enum("line", "scatter")
   
    # This "view" attribute defines how an instance of this class will
    # be displayed when .edit_traits() is called on it.  (See MyApp.OnInit()
    # below.)
    view = View(ChacoPlotItem("index", "data",
                               type_trait="plot_type",
                               resizable=True,
                               x_label="Time",
                               y_label="Signal",
                               color="blue",
                               bgcolor="white",
                               border_visible=True,
                               border_width=1,
                               padding_bg_color="lightgray",
                               width=800,
                               height=380,
                               show_label=False),
                HGroup(spring, Item("plot_type", style='custom'), spring),
                resizable = True,
                width=800, height=500)


class HeliPlotter(HasTraits):
    
    # A reference to the plot viewer object
    viewer = Instance(HeliDisplay)
   
    scantype = Int(2)
    channel = Int(0)
    scanrate = Float(100.0)
   
    # The max number of data points to accumulate and show in the plot
    max_num_points = Int(1000)
   
    # The number of data points we have received; we need to keep track of
    # this in order to generate the correct x axis data series.
    num_ticks = Int(0)
   
    view = View(Group('scantype', 
                      'channel',
                      'scanrate',
                      'max_num_points',
                      orientation="vertical"),
                      buttons=["Close"])
   
    def plot_data(self, datadict):
        
        if not datadict.has_key(self.scantype):
            print "discarding scan types %s" % str(datadict.keys())
            return
            
        typedata = datadict[self.scantype]
        if typedata.shape[1] <= self.channel:
            print "not enough channels, type %d has %d chs" % (self.scantype, typedata.shape[1])
            return
            
        chdata=typedata[:,self.channel]
        
        chlen=len(chdata)
        self.num_ticks += chlen
       
        # grab the existing data, truncate it, and append the new points
        cur_data = self.viewer.data
        new_data = np.concatenate((cur_data[-self.max_num_points+chlen:], chdata))
        
        firstx = (self.num_ticks - len(new_data) + 1) / self.scanrate        
        lastx = (self.num_ticks+0.01) / self.scanrate        
        new_index = np.arange(firstx, lastx, 1.0/self.scanrate)
        
        self.viewer.index = new_index
        self.viewer.data = new_data
        return
        
    def _scantype_changed(self):
        self.clear_data()
        
    def _channel_changed(self):
        self.clear_data()
        
    def clear_data(self):
        self.viewer.data = np.zeros(0)
        self.viewer.index = np.zeros(0)
        
           