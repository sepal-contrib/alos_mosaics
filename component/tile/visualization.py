### TILE SHOWING THE RESULTS

from sepal_ui import sepalwidgets as sw
from sepal_ui import mapping as sm
import ipyvuetify as v

from component.message import ms
from component.scripts import * 
from component import parameter as pm

# create an empty result tile that will be filled with displayable plot, map, links, text
class VisualizationTile(sw.Tile):
    
    def __init__(self, aoi_model, model, **kwargs):
        
        # gather the model
        self.aoi_model = aoi_model
        self.model = model
        
        # widgets
        self.visSelect = v.RadioGroup(
            v_model = pm.layer_select[0]['value'],
            children = [v.Radio(key=e['key'], label=e['label'], value=e['value']) for e in pm.layer_select]
        )
            
        # add the widgets 
        self.m = sm.SepalMap()
        
        # bindings
        self.model.bind(self.visSelect, 'viz')
        
        # construct the Tile with the widget we have initialized 
        super().__init__(
            id_    = "visualization_widget", # the id will be used to make the Tile appear and disapear
            title  = ms.visualization.title, # the Title will be displayed on the top of the tile
            inputs = [self.visSelect, self.m],#self.asset,
            alert = sw.Alert()
        )
        
        self.visSelect.observe(self._on_change, 'v_model')
        
    def _on_change(self, change):
        
        if self.model.viz == 'RGB' and self.model.dB:
            dataset = self.model.dataset.select(['HH', 'HV', 'HHHV_ratio'])
            viz = pm.visParamdB
        elif self.model.viz == 'RGB' and not self.model.dB:            
            dataset = self.model.dataset.select(['HH', 'HV', 'HHHV_ratio'])
            viz = pm.visParamPow
        elif self.model.viz == 'RFDI':
            dataset = self.model.dataset.select(['RFDI'])
            viz = pm.visParamRFDI
        elif self.model.viz == 'FNF' and int(str(self.model.year)) <= 2017:
            dataset = self.model.dataset.select(['fnf_'+ str(self.model.year)])
            viz = pm.visParamFNF
            
        # Display the map
        display_result(
            self.aoi_model.feature_collection,
            dataset,
            self.m, 
            viz
        )
        
        
