import ee
from . import _quegan, _refined_lee

from component.message import ms


def create(
    region,
    year,
    output,
    speckle_filter="NONE",
    speckle_filter_dict={"radius": 30, "units": "meters"},
    ls_mask=True,
    db=True,
):
    def set_resample(image):
        """Set resampling of the image to bilinear"""
        return image.resample()

    def mask_ls(image):

        ls_mask = image.select("qa").neq(100).bitwiseAnd(image.select("qa").neq(150))
        return image.updateMask(ls_mask)

    def psr_calibrate(image):
        calibrated = ee.Image(10.0).pow(
            (image.select(["HH", "HV"]).log10().multiply(2.0)).subtract(8.3)
        )

        return image.addBands(calibrated, None, True)

    def to_db(image):

        db_bands = (
            ee.Image(10)
            .multiply(image.select(["HH", "HV"]).log10())
            .rename(["HH", "HV"])
        )
        return image.addBands(db_bands, None, True)

    def boxcar_filter(image):

        filtered = (
            image.select(["HH", "HV"])
            .reduceNeighborhood(
                ee.Reducer.mean(),
                ee.Kernel.square(
                    speckle_filter_dict["radius"], speckle_filter_dict["units"]
                ),
            )
            .rename(["HH", "HV"])
        )

        return image.addBands(filtered, None, True)

    collection = (
        ee.ImageCollection("JAXA/ALOS/PALSAR/YEARLY/SAR")
        .map(psr_calibrate)
        .map(set_resample)
    )

    if speckle_filter == "QUEGAN":
        collection = _quegan.apply(collection, speckle_filter_dict)

    image = collection.filter(
        ee.Filter.date(str(year) + "-01-01", str(year) + "-12-31")
    ).first()

    if speckle_filter == "BOXCAR":
        image = boxcar_filter(image)

    if speckle_filter == "REFINED_LEE":
        image = _refined_lee.apply(image)

    if ls_mask:
        image = mask_ls(image)

    image = image.addBands(
        image.select("HH").divide(image.select("HV")).rename("HHHV_ratio")
    )

    image = image.addBands(image.normalizedDifference(["HH", "HV"]).rename("RFDI"))

    image_100 = image.select(["HH", "HV"]).multiply(ee.Image(100)).toInt16()
    texture_hh = image_100.select("HH").glcmTexture(7)
    texture_hv = image_100.select("HV").glcmTexture(7)
    image = image.addBands(texture_hh.select("HH_var", "HH_idm", "HH_diss")).addBands(
        texture_hv.select("HV_var", "HV_idm", "HV_diss")
    )

    if db:
        image = to_db(image)

    # let the user know that you managed to do something
    output.add_live_msg(ms.process.end_computation, "success")

    # add fnf band
    if year <= 2017:
        fnf_image = (
            ee.ImageCollection("JAXA/ALOS/PALSAR/YEARLY/FNF")
            .filter(ee.Filter.date(str(year) + "-01-01", str(year) + "-12-31"))
            .first()
            .rename("fnf_" + str(year))
        )

        image = image.addBands(fnf_image)

    # remove aux bands if not explicetly set to True
    # if not aux:
    #    nameOfBands = image.bandNames().getInfo()
    #    nameOfBands.remove('qa')
    #    nameOfBands.remove('date')
    #    nameOfBands.remove('angle')

    return image.clip(region)
