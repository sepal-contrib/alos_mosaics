# It is strongly suggested to use a separate file to define the tiles of your process and then call them in your notebooks. 
# it will help you to have control over their fonctionalities using object oriented programming

from sepal_ui import sepalwidgets as sw
import ipyvuetify as v

from component import scripts
from component.message import ms
from component import parameter as pm

# the tiles should all be heriting from the sepal_ui Tile object 
# if you want to create extra reusable object, you can define them in an extra widget.py file 
class ProcessTile(sw.Tile):
    
    def __init__(self, io, aoi_io, result_tile, **kwargs):
        
        # Define the io and the aoi_io as class attribute so that they can be manipulated in its custom methods
        self.io = io 
        self.aoi_io = aoi_io
        
        # LINK to the result tile 
        self.result_tile = result_tile
        
        # WIDGETS
        self.year   = v.Select(
            label   = ms.process.slider,
            v_model = None,
            items   = pm.years
        )
        
        self.filter = v.Select(
            label   = ms.process.speckle,
            v_model = None,
            items = pm.speckle_filters            
        )
        
        self.rfdi = v.Switch(
            class_  = "ml-5",
            label   = ms.process.rfdi,
            v_model = True
        )
        
        self.ls_mask = v.Switch(
            class_  = "ml-5",
            label   = ms.process.ls_mask,
            v_model = True
        )
        
        self.dB = v.Switch(
            class_  = "ml-5",
            label   = ms.process.dB,
            v_model = True
        )
        
        #self.asset  = v.TextField(
        #    label   = ms.process.textfield,
        #    v_model = None
        #)
        
        # create the output alert 
        # this component will be used to display information to the end user when you lanch the process
        # it's hidden by default 
        # it also has the embeded `bind` method that link mutable variable to component v_model
        # bind return self so it can be chained to bind everything in one statement. 
        # args are (widget, io, io_attribute_name)
        self.output = sw.Alert() \
            .bind(self.year, self.io, 'year')  \
            .bind(self.filter, self.io, 'speckle')\
            .bind(self.rfdi, self.io, 'rfdi')\
            .bind(self.ls_mask, self.io, 'ls_mask')\
            .bind(self.dB, self.io, 'dB')
            #.bind(self.asset, self.io, 'asset')\
            
        # to launch the process you'll need a btn 
        # here it is as a special sw widget (the message and the icon can also be customized see sepal_ui widget doc)
        self.btn = sw.Btn()
        
        # construct the Tile with the widget we have initialized 
        super().__init__(
            id_    = "process_widget", # the id will be used to make the Tile appear and disapear
            title  = ms.process.title, # the Title will be displayed on the top of the tile
            inputs = [self.year,self.filter, self.rfdi, self.ls_mask, self.dB],#self.asset,
            btn    = self.btn,
            output = self.output
        )
        
        # now that the Tile is created we can link it to a specific function
        self.btn.on_event("click", self._on_run)
        
    # PROCESS AFTER ACTIVATING BUTTON
    def _on_run(self, widget, data, event): 
            
        # toggle the loading button (ensure that the user doesn't launch the process multiple times)
        widget.toggle_loading()
            
        # check that the input that you're gonna use are set (Not mandatory)
        if not self.output.check_input(self.aoi_io.get_aoi_name(), ms.process.no_aoi):       return widget.toggle_loading()
        if not self.output.check_input(self.io.year,               ms.process.no_slider):    return widget.toggle_loading()
        #if not self.output.check_input(self.io.asset,              ms.process.no_textfield): return widget.toggle_loading()
        
        
        # Wrap the process in a try/catch statement 
        try:
            
            # Create the mosaic
            dataset = scripts.create(
                self.aoi_io.get_aoi_ee(),
                self.io.year,
                self.output,
                speckle_filter=self.io.filter,
                add_rfdi=self.io.rfdi,
                ls_mask=self.io.ls_mask,
                db=self.io.dB
            ) 
            
            # Display the map
            m = scripts.display_result(
                self.aoi_io.get_aoi_ee(),
                dataset,
                self.result_tile.m
            )
            
            # change the io values as its a mutable object 
            # useful if the io is used as an input in another tile
            self.io.dataset = dataset
            
            # release the export btn
            self.result_tile.btn.disabled = False
            
            # conclude the computation with a message
            self.output.add_live_msg(ms.process.end_computation, 'success')
            
        except Exception as e: 
            self.output.add_live_msg(str(e), 'error')
        
        # release the btn
        widget.toggle_loading()
        
        return
        
        