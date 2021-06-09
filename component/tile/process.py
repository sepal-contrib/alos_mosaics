# It is strongly suggested to use a separate file to define the tiles of your process and then call them in your notebooks. 
# it will help you to have control over their fonctionalities using object oriented programming

from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su
import ipyvuetify as v

from component import scripts
from component.message import ms
from component import parameter as pm

# the tiles should all be heriting from the sepal_ui Tile object 
# if you want to create extra reusable object, you can define them in an extra widget.py file 
class ProcessTile(sw.Tile):
    
    def __init__(self, model, aoi_model, viz_tile, export_tile, **kwargs):
        
        # Define the model and the aoi_model as class attribute so that they can be manipulated in its custom methods
        self.model = model 
        self.aoi_model = aoi_model
        
        # LINK to the result tile 
        self.viz_tile = viz_tile
        self.export_tile = export_tile
        
        # WIDGETS
        self.year   = v.Select(
            label   = ms.process.slider,
            v_model = None,
            items   = pm.years[::-1]
        )
        
        self.filter = v.Select(
            label   = ms.process.filter,
            v_model = None,
            items = pm.speckle_filters            
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
         
        # it also has the embeded `bind` method that link mutable variable to component v_model
        # bind return self so it can be chained to bind everything in one statement. 
        # args are (widget, model, model_attribute_name)
        self.model \
            .bind(self.year, 'year')  \
            .bind(self.filter, 'filter') \
            .bind(self.ls_mask, 'ls_mask') \
            .bind(self.dB, 'dB')
        
        # construct the Tile with the widget we have initialized 
        super().__init__(
            id_    = "process_widget", # the id will be used to make the Tile appear and disapear
            title  = ms.process.title, # the Title will be displayed on the top of the tile
            inputs = [self.year, self.filter, self.ls_mask, self.dB],#self.asset,
            btn    = sw.Btn(ms.process.process),
            alert = sw.Alert()
        )
        
        # now that the Tile is created we can link it to a specific function
        self.btn.on_event("click", self._on_run)
        
    @su.loading_button(debug=False)
    def _on_run(self, widget, data, event): 
            
        # toggle the loading button (ensure that the user doesn't launch the process multiple times)
        widget.toggle_loading()
            
        # check that the input that you're gonna use are set (Not mandatory)
        if not self.alert.check_input(self.aoi_model.name, ms.process.no_aoi): return widget.toggle_loading()
        if not self.alert.check_input(self.model.year, ms.process.no_slider): return widget.toggle_loading()
            
        # Create the mosaic
        dataset = scripts.create(
            self.aoi_model.feature_collection,
            self.model.year,
            self.alert,
            speckle_filter=self.model.filter,
            ls_mask=self.model.ls_mask,
            db=self.model.dB
        )

        # change the model values as its a mutable object 
        # useful if the model is used as an input in another tile
        self.model.dataset = dataset

        # release the export btn
        self.export_tile.asset_btn.disabled = False
        self.export_tile.sepal_btn.disabled = False

        # conclude the computation with a message
        self.alert.add_live_msg(ms.process.end_computation, 'success')

        # launch vizualisation
        self.viz_tile._on_change(None)
        
        # release the btn
        widget.toggle_loading()
        
        return
        
        