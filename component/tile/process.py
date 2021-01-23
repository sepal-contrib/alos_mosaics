# It is strongly suggested to use a separate file to define the tiles of your process and then call them in your notebooks. 
# it will help you to have control over their fonctionalities using object oriented programming

from sepal_ui import sepalwidgets as sw
import ipyvuetify as v

from .. import scripts
from ..message import ms

# the tiles should all be heriting from the sepal_ui Tile object 
# if you want to create extra reusable object, you can define them in an extra widget.py file 
class ProcessTile(sw.Tile):
    
    def __init__(self, io, aoi_io, result_tile, **kwargs):
        
        # define the io and the aoi_io as class attribute so that they can be manipulated in its custom methods
        self.io = io 
        self.aoi_io = aoi_io
        
        # as I will display my results in another tile I also link it to the result tile 
        self.result_tile = result_tile
        
        # create all the widgets that you want to use in the tile
        # create the widgets following ipyvuetify lib requirements (more information in the ipyvuetify and sepal_ui doc)
        # if you want to use them in custom function you should consider adding them in the class attirbute
        self.year = v.Slider(
            label       = ms.process.slider, 
            class_      = "mt-5", 
            thumb_label = True, 
            v_model     = None,
            min         = 2015,
            max         = 2018,
            value       = 2015
        )
        
        self.asset_basename = v.TextField(
            label   = ms.process.textfield, 
            v_model = None
        )
        
        # create the output alert 
        # this component will be used to display information to the end user when you lanch the process
        # it's hidden by default 
        # it also has the embeded `bind` method that link mutable variable to component v_model
        # bind return self so it can be chained to bind everything in one statement. 
        # args are (widget, io, io_attribute_name)
        self.output = sw.Alert() \
            .bind(self.year, self.io, 'year_value')  \
            .bind(self.asset_basename, self.io, 'asset_basename_value')
        
        # to launch the process you'll need a btn 
        # here it is as a special sw widget (the message and the icon can also be customized see sepal_ui widget doc)
        self.btn = sw.Btn()
        
        # construct the Tile with the widget we have initialized 
        super().__init__(
            id_    = "process_widget", # the id will be used to make the Tile appear and disapear
            title  = ms.process.title, # the Title will be displayed on the top of the tile
            inputs = [self.year,self.asset_basename],
            btn    = self.btn,
            output = self.output
        )
        
        # now that the Tile is created we can link it to a specific function
        self.btn.on_event('click', self._on_run)
        
    # in the pep 8 convention, "_" in the beggining of a method name
    # specify that the function is not supposed to be called outside the class (same as private declaration in C/C++)
    # the 3 parameters (widget, data, event) are the mandatory parameters of the javascript callback, we will only use widget
    def _on_run(self, widget, data, event): 
            
        # toggle the loading button (ensure that the user doesn't launch the process multiple times)
        widget.toggle_loading()
            
        # check that the input that you're gonna use are set (Not mandatory)
        if not self.output.check_input(self.aoi_io.get_aoi_name(),     ms.process.no_aoi):       return widget.toggle_loading()
        if not self.output.check_input(self.io.year_value,             ms.process.no_slider):    return widget.toggle_loading()
        if not self.output.check_input(self.io.asset_basename_value,   ms.process.no_textfield): return widget.toggle_loading()
        
        
        # Wrap the process in a try catch statement 
        try:
            
            # Create the mosaic
            dataset = scripts.create_mosaic(
                self.output,
                self.aoi_io.get_aoi_ee(),
                self.io.year_value
               )
                
                
            # Create the asset name
            gee_asset = scripts.asset_name(
                self.io.asset_basename_value)
            
            
            # Display the map
            m = scripts.display_result(
                self.aoi_io.get_aoi_ee(),
                dataset)
            
            
            # display the map in the result tile 
            content = [sw.Btn(ms.process.gee_btn,gee_asset),m]  #str(csv_path)
            self.result_tile.set_content(content) # content of a tile can be changed dynamically 
            
            
            # change the io values as its a mutable object 
            # useful if the io is used as an input in another tile
            self.io.csv_path = gee_asset #csv_path
            
            # conclude the computation with a message
            self.output.add_live_msg(ms.process.end_computation, 'success')
            
        except Exception as e: 
            self.output.add_live_msg(str(e), 'error')
        
        # release the btn
        widget.toggle_loading()
        
        return
        
        