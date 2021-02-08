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

from .filters import *
from .gee import *
from .gdrive import *

ee.Initialize()

def alos_kc_mosaic(ee_aoi, year, output, mt_speck):
    
    # we call the collection and apply the pre-processing steps
    collection = ee.ImageCollection('JAXA/ALOS/PALSAR/YEARLY/SAR') \
                    .filterBounds(ee_aoi) \
                    .map(applyCalibration) \
                    .map(setresample)

    # if we choose to speckle filter
    if mt_speck:
        image = mtDespeck(collection, 30, 'meters').filter(ee.Filter.date(f'{year}-01-01', f'{year}-12-31')).first().clip(ee_aoi)          
    else: 
        image = collection.filter(ee.Filter.date(f'{year}-01-01', f'{year}-12-31')).first().clip(ee_aoi)
        
    # to dB scale
    image = toDb(ee.Image(image))
    
    # add ratio band
    image = image.addBands(image.select('HH').subtract(image.select('HV')).rename('HHHV_ratio'));
    
    # fake the loading of something so that the user see the btn spining
    time.sleep(0.1)
    
    # let the user know that you managed to do something
    output.add_live_msg(ms.process.end_computation, 'success')
    
    return image

def display_result(ee_aoi, dataset, m, db):
    """
    Display the results on the map 
    
    Args:
        ee_aoi: (ee.Geometry): the geometry of the aoi
        dataset (ee.Image): the image the display
        m (sw.SepalMap): the map used for the display
        db (bool): either to use the db scale or not
        
    Return:
        (sw.SepalMap): the map with the different layers added
    """
    # AOI borders in blue 
    empty   = ee.Image().byte()
    outline = empty.paint(featureCollection = ee_aoi, color = 1, width = 3)
   
    # Zoom to AOI
    m.zoom_ee_object(ee_aoi.geometry())
    
    # Add objects
    m.addLayer(outline, {'palette': v.theme.themes.dark.info}, 'aoi')
    if db:
        m.addLayer(dataset, pm.VisParam , ms.process.alos_mosaic) 
    else:
        m.addLayer(dataset, pm.VisParamPow , ms.process.alos_mosaic) 
       
    return m
    

def export_to_asset(aoi_io, dataset, filename, output):
    """
    Export the dataset as an asset in GEE
    
     Args: 
        aoi_io (sw.Aoi_io): the aoi to clip on
        dataset (ee.Image): the image to export 
        filename (str): the name of the final file
        output (sw.Alert): the alert used to display informations to the end user
        
    return: 
        (str): asset link
        
    """
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
        'maxPixels': 1e13
    }
    
    task = ee.batch.Export.image.toAsset(**task_config)
    task.start()
       
    output.add_live_msg(ms.process.task_start)
    
    # tell me if you want to display the exportation status live or not
    
    return asset_name

def export_to_sepal(aoi_io, dataset, filename, output):
    """
    Export the dataset to gdrive and then to sepal. All buffer files will be deleted
    
    Args: 
        aoi_io (sw.Aoi_io): the aoi to clip on
        dataset (ee.Image): the image to export 
        filename (str): the name of the final file
        output (sw.Alert): the alert used to display informations to the end user
        
    return: 
        (str): download pathname
        
    """
    
    output.add_live_msg(ms.download.start_download)
    
    # get the root folder of the user 
    folder = Path(ee.data.getAssetRoots()[0]['id'])
    asset_name = folder.joinpath(filename)
        
    # load the drive_handler
    drive_handler = gdrive()
    
    # clip the image
    dataset = dataset.clip(aoi_io.get_aoi_ee())
        
    # download the tiled files
    downloads = drive_handler.download_to_disk(filename, dataset, aoi_io, output)
        
    # wait for the end of the download process
    if downloads:
        wait_for_completion([filename], output)
    output.add_live_msg(ms.gee.tasks_completed, 'success') 
    
    # create merge name 
    filename_merge = pm.result_dir.joinpath(f'{filename}_merge.tif')

    # digest the tiles
    digest_tiles(aoi_io, filename, pm.result_dir, output, filename_merge)
        
    output.add_live_msg(ms.download.remove_gdrive)
    # remove the files from drive
    drive_handler.delete_files(drive_handler.get_files(filename))
        
    # display msg 
    output.add_live_msg(ms.download.completed, 'success')

    return filename_merge
    
    