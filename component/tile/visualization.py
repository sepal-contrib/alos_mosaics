### TILE SHOWING THE RESULTS

from sepal_ui import sepalwidgets as sw
from sepal_ui import mapping as sm
import ipyvuetify as v

from component.message import ms
from component.scripts import * 
from component import parameter as pm

# create an empty result tile that will be filled with displayable plot, map, links, text
class VisualizationTile(sw.Tile):
    
    def __init__(self, aoi_io, io, **kwargs):
        
        # gather the io
        self.aoi_io = aoi_io
        self.io = io
        
        # create an output alert 
        self.output = sw.Alert()
        
        # 
        
        self.visSelect = v.RadioGroup(
            v_model = pm.layer_select[0]['value'],
            children = [v.Radio(key=e['key'], label=e['label'], value=e['value']) for e in pm.layer_select]
        )
            
        # add the widgets 
        self.m = sm.SepalMap()
        
        # bindings
        self.output = sw.Alert() \
            .bind(self.visSelect, self.io, 'viz')
        
        # construct the Tile with the widget we have initialized 
        super().__init__(
            id_    = "visualization_widget", # the id will be used to make the Tile appear and disapear
            title  = ms.visualization.title, # the Title will be displayed on the top of the tile
            inputs = [self.visSelect, self.m],#self.asset,
            output = self.output
        )
        
        self.visSelect.observe(self._on_change, 'v_model')
        
    def _on_change(self, change):
        
        if self.io.viz == 'RGB' and self.io.dB:
            dataset = self.io.dataset.select(['HH', 'HV', 'HHHV_ratio'])
            viz = pm.visParamdB
        elif self.io.viz == 'RGB' and not self.io.dB:            
            dataset = self.io.dataset.select(['HH', 'HV', 'HHHV_ratio'])
            viz = pm.visParamPow
        elif self.io.viz == 'RFDI':
            dataset = self.io.dataset.select(['RFDI'])
            viz = pm.visParamRFDI
        elif self.io.viz == 'FNF':
            dataset = self.io.dataset.select(['fnf_'+ str(self.io.year)])
            viz = pm.visParamFNF
            
        # Display the map
        display_result(
            self.aoi_io.get_aoi_ee(),
            dataset,
            self.m, 
            viz
        )
        
        
