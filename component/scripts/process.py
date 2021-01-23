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

from ..message import ms

ee.Initialize()

def create_mosaic(output, ee_aoi, year):

    # GEE script
    my_year    = str(year)
    
    ### NEED TO ADD HERE THE SPECKLE FILTERING AND CALIBRATION
         
    collection = ee.ImageCollection('JAXA/ALOS/PALSAR/YEARLY/SAR').filterBounds(ee_aoi)#.map(applyCalibration).map(setresample)
    dataset    = collection.filter(ee.Filter.date(my_year + '-01-01', my_year + '-12-31')).first().clip(ee_aoi)
     
    # fake the loading of something so that the user see the btn spining
    time.sleep(1)
    
    # let the user know that you managed to do something
    output.add_live_msg(ms.process.end_computation, 'success')
    
    return dataset



def asset_name(asset_basename):

    # MODIFY/CUSTOMIZE/LINK WITH ASSET REPOSITORY
    asset_name = 'users/dannunzio/' + asset_basename
    return asset_name



def display_result(ee_aoi,dataset):
    
    # Setup a map with AOI + mosaic
    m = SepalMap(['CartoDB.DarkMatter']) # you can choose in all the available basemaps of leaflet 
        
    # AOI borders in blue 
    empty   = ee.Image().byte()
    outline = empty.paint(featureCollection = ee_aoi, color = 1, width = 3)
    
    # ALOS Mosaic parameters
    VisParam   = {"opacity":1,"bands":["HH","HV","HH"],"min":160.36,"max":7857.64,"gamma":1};

    # Zoom to AOI
    m.zoom_ee_object(ee_aoi.geometry())
    
    # Add objects
    m.addLayer(outline, {'palette': v.theme.themes.dark.info}, 'aoi')
    m.addLayer(dataset,VisParam , ms.process.alos_mosaic) 
       
    return m
    

def export_result(dataset,asset_name):
        
        ### NEED TO ADD HERE THE EXPORT TO ASSET FUNCTION
    return asset_name
    
    