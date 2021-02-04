import ee
ee.Initialize()

def setresample(image):
    return image.resample()

def toDb(image):
    db = ee.Image(10).multiply(image.select(['HH', 'HV']).log10())
    return ee.Image(db.copyProperties(image))

def applyCalibration(image):

    def psrCalibrate(img):
        return ee.Image(10.0).pow((img.log10().multiply(2.0)).subtract(8.3))

    def onBand(band):
        return image.addBands(psrCalibrate(image.select(band)).rename(band), None, True)

    image = onBand('HH')
    image = onBand('HV')
    return image

def mtDespeck(images, radius, units):
    
    def mapMeanSpace(image):
        reducer = ee.Reducer.mean()
        kernel = ee.Kernel.square(radius, units)
        mean = image.reduceNeighborhood(reducer, kernel).rename(meanBand)
        ratio = image.divide(mean).rename(ratioBand)
        return image.addBands(mean).addBands(ratio).copyProperties(image)

    bands = images.first().bandNames()

    def cat_mean(bandName):
        return ee.String(bandName).cat('_mean')
    def cat_ratio(bandName):
        return ee.String(bandName).cat('_ratio')

    meanBand  = bands.map(cat_mean)
    ratioBand = bands.map(cat_ratio)

    # compute spatial average for all images
    meanSpace = images.map(mapMeanSpace)

    def mtDespeckSingle(image):
        angle      = image.select('angle')
        meanSpace2 = ee.ImageCollection(meanSpace).select(ratioBand)
        b = image.select(meanBand)
        return (b.multiply(meanSpace2.sum()).divide(meanSpace2.count()).rename(bands)).copyProperties(image).set('system:time_start', image.get('system:time_start'))

    return meanSpace.map(mtDespeckSingle)

