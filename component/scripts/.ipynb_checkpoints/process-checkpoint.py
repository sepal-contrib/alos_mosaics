import time
import sys
import os
from pathlib import Path

import numpy as np
import pandas as pd
import geemap
import ee
import ipyvuetify as v
from matplotlib import pyplot as plt
from ipywidgets import Output

from sepal_ui.mapping import SepalMap

from component.message import ms
from component import parameter as pm

ee.Initialize()

def create_mosaic(ee_aoi, year, output):

    # GEE script
    my_year = str(year)
    
    ### NEED TO ADD HERE THE SPECKLE FILTERING AND CALIBRATION
         
    collection = ee.ImageCollection('JAXA/ALOS/PALSAR/YEARLY/SAR').filterBounds(ee_aoi)#.map(applyCalibration).map(setresample)
    dataset    = collection.filter(ee.Filter.date(f'{year}-01-01', f'{year}-12-31')).first().clip(ee_aoi)
     
    # fake the loading of something so that the user see the btn spining
    time.sleep(1)
    
    # let the user know that you managed to do something
    output.add_live_msg(ms.process.end_computation, 'success')
    
    return dataset

def display_result(ee_aoi,dataset, m):
        
    # AOI borders in blue 
    empty   = ee.Image().byte()
    outline = empty.paint(featureCollection = ee_aoi, color = 1, width = 3)
    
    # Zoom to AOI
    m.zoom_ee_object(ee_aoi.geometry())
    
    # Add objects
    m.addLayer(outline, {'palette': v.theme.themes.dark.info}, 'aoi')
    m.addLayer(dataset, pm.VisParam , ms.process.alos_mosaic) 
       
    return m
    

def export_result(aoi_io, dataset, filename, output):
    
    # get the root folder of the user 
    folder = Path(ee.data.getAssetRoots()[0]['id'])
    asset_name = folder.joinpath(filename)
    # launch the export
    task_config = {
        'image': dataset,
        'description': filename,
        'assetId': str(asset_name),
        'scale': 30, # we need to change this scale for big surfaces 
        'region': aoi_io.get_aoi_ee().geometry(),
        'pyramidingPolicy': {'.default': 'sample'},
        'maxPixels': 1e12
    }
    
    task = ee.batch.Export.image.toAsset(**task_config)
    task.start()
       
    output.add_live_msg(ms.process.task_start)
    
    # tell me if you want to display the exportation status live or not
    
    return asset_name
    
    