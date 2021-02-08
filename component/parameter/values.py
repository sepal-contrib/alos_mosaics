# minimum year for the ALOS images 
min_year = 2015

# maximum year for the ALOS images 
max_year = 2017

# replacement to select from all possibile (AV)
years = [2007, 2008, 2009, 2010, 2015, 2016, 2017]

# speckle filters to select from
speckle_filters = [
    {'text': 'No Speckle filter', 'value': 'NONE'}, 
    {'text': 'Refined Lee (zoom dependent)', 'value': 'REFINED_LEE'},
    {'text': 'Quegan Filter', 'value': 'QUEGAN'}
]

# name of the file in the output directory 
def asset_name(aoi_io, io):
    """return the standard name of your asset/file"""
    
    filename = f"alos_mosaic_{aoi_io.get_aoi_name()}_{io.year}"
    
    if io.filter != 'NONE':
        filename += f"_{io.filter.lower()}"
        
    if io.rfdi:
        filename += '_rfdi'
        
    if io.ls_mask:
        filename += '_masked'
        
    if io.dB:
        filename += '_dB'
    
    return filename