import time
import ee
from . import _quegan, _refined_lee

import ipyvuetify as v

from matplotlib import pyplot as plt
from ipywidgets import Output

from sepal_ui.mapping import SepalMap

from component.message import ms
from component import parameter as pm

def create(
        region,
        year,
        output,
        speckle_filter='NONE',
        speckle_filter_dict={'radius': 30, 'units': 'meters'},
        ls_mask=True,
        add_ratio=True,
        add_rfdi=True,
        db=True
):

    def set_resample(image):
        """ Set resampling of the image to bilinear"""
        return image.resample()

    def mask_ls(image):

        ls_mask = image.select('qa').neq(100)\
            .bitwiseAnd(image.select('qa').neq(150))
        return image.updateMask(ls_mask)

    def psr_calibrate(image):
        calibrated = ee.Image(10.0)\
            .pow((image.select(['HH', 'HV']).log10().multiply(2.0)).subtract(8.3))

        return image.addBands(calibrated, None, True)

    def to_db(image):

        db_bands = ee.Image(10).multiply(image.select(['HH', 'HV']).log10())\
            .rename(['HH', 'HV'])
        return image.addBands(db_bands, None, True)

    def boxcar_filter(image):

        filtered = image.select(['HH', 'HV']) \
            .reduceNeighborhood(
                ee.Reducer.mean(),
                ee.Kernel.square(
                    speckle_filter_dict['radius'], speckle_filter_dict['units']
                )
        ).rename(['HH', 'HV'])

        return image.addBands(filtered, None, True)

    collection = ee.ImageCollection('JAXA/ALOS/PALSAR/YEARLY/SAR')\
        .map(psr_calibrate)\
        .map(set_resample)

    if speckle_filter == 'QUEGAN':
        collection = _quegan.apply(collection, speckle_filter_dict)

    image = collection.filter(
        ee.Filter.date(str(year) + '-01-01', str(year) + '-12-31')
    ).first()

    if speckle_filter == 'BOXCAR':
        image = boxcar_filter(image)

    if speckle_filter == 'REFINED_LEE':
        image = _refined_lee.apply(image)

    if ls_mask:
        image = mask_ls(image)

    if add_ratio:
        image = image.addBands(
            image.select('HH').divide(image.select('HV')).rename('HHHV_ratio')
        )

    if add_rfdi:
        image = image.addBands(
            image.normalizedDifference(['HH', 'HV']).rename('RFDI')
        )

    if db:
        image = to_db(image)

    # fake the loading of something so that the user see the btn spining
    time.sleep(0.1)
    
    # let the user know that you managed to do something
    output.add_live_msg(ms.process.end_computation, 'success')
    
    return image.clip(region)
