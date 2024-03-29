# possible years to select from
years = [2007, 2008, 2009, 2010, 2015, 2016, 2017, 2018, 2019, 2020]
last_fnf_year = 2017

# speckle filters to select from
speckle_filters = [
    {"text": "No Speckle filter", "value": "NONE"},
    {"text": "Refined Lee (zoom dependent)", "value": "REFINED_LEE"},
    {"text": "Quegan Filter", "value": "QUEGAN"},
]

layer_select = [
    {"label": "Backscatter RGB (HH, HV, HH/HV power ratio)", "value": "RGB"},
    {
        "label": "Radar Forest Degradation Index (RFDI, Mitchard et al. 2012)",
        "value": "RFDI",
    },
    {
        "label": "Forest/Non-Forest (available only until 2017)",
        "value": "FNF",
    },  # fnf need to remain the last one
]


# name of the file in the output directory
def asset_name(aoi_model, model, fnf=False):
    """return the standard name of your asset/file"""

    prefix = "kc_fnf" if fnf else "alos_mosaic"
    filename = f"{prefix}_{aoi_model.name}_{model.year}"

    if model.filter != "NONE":
        filename += f"_{model.filter.lower()}"

    if model.rfdi:
        filename += "_rfdi"

    if model.ls_mask:
        filename += "_masked"

    if model.dB:
        filename += "_dB"

    if model.texture:
        filename += "_texture"

    if model.aux:
        filename += "_aux"

    return filename
