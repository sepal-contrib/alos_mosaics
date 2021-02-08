### TILE SHOWING THE RESULTS

from sepal_ui import sepalwidgets as sw
from sepal_ui import mapping as sm
import ipyvuetify as v

from component.message import ms
from component.scripts import * 
from component import parameter as cp

# create an empty result tile that will be filled with displayable plot, map, links, text
class ResultTile(sw.Tile):
    
    def __init__(self, aoi_io, io, **kwargs):
        
        # gather the io
        self.aoi_io = aoi_io
        self.io = io
        
        # create an output alert 
        self.output = sw.Alert()
        
        # add a btn and a map 
        self.m = sm.SepalMap()
        self.asset_btn = sw.Btn('export to asset', 'mdi-download', disabled=True, class_='ma-5')
        self.sepal_btn = sw.Btn('export to sepal', 'mdi-download', disabled = True, class_='ma-5')
        
        # note that btn and output are not a madatory attributes 
        super().__init__(
            id_ = "result_widget",
            title = ms.result.title,
            inputs = [self.m],
            output = self.output,
            btn = v.Layout(row=True, children = [self.asset_btn, self.sepal_btn])
        )
        
        #link the btn 
        self.asset_btn.on_event('click', self._on_asset_click)
        
    def _on_asset_click(self, widget, data, event):
        
        widget.toggle_loading()
        
        try:
            # export the results 
            asset_id = export_to_asset(
                self.aoi_io, 
                self.io.dataset, 
                cp.asset_name(self.aoi_io.get_aoi_name(), self.io.year), 
                self.output
            )
        
            # display a message 
            self.output.add_live_msg(ms.process.task_launched.format(asset_id), 'success')
        
        except Exception as e:
            self.output.add_live_msg(str(e), 'error')
            
        widget.toggle_loading()
        
        return
    
    def _on_sepal_click(self, widget, data, event):
        
        widget.toggle_loading()
        
        try:
            # export the results 
            asset_id = export_to_sepal(
                self.aoi_io, 
                self.io.dataset, 
                cp.asset_name(self.aoi_io.get_aoi_name(), self.io.year), 
                self.output
            )
        
        except Exception as e:
            self.output.add_live_msg(str(e), 'error')
            
        widget.toggle_loading()
        
        return