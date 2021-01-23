{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "    def setresample(image):\n",
    "        return image.resample()\n",
    "\n",
    "    def toDb(image):\n",
    "        db = ee.Image(10).multiply(image.select(['HH', 'HV']).log10())\n",
    "        return ee.Image(db.copyProperties(image))\n",
    "    \n",
    "    def toLinearScale(band):\n",
    "        return ee.Image(10).pow(band.divide(10))\n",
    "    \n",
    "    def toDb(band):\n",
    "        return band.log10().multiply(10)\n",
    "        \n",
    "    def applyCalibration(image):\n",
    "    \n",
    "        def psrCalibrate(img):\n",
    "            return ee.Image(10.0).pow((img.log10().multiply(2.0)).subtract(8.3))\n",
    "    \n",
    "        def onBand(band):\n",
    "            return image.addBands(psrCalibrate(image.select(band)).rename(band), null, true)\n",
    "        \n",
    "        image = onBand('HH')\n",
    "        image = onBand('HV')\n",
    "        return image\n",
    "    \n",
    "    def toDb(band):\n",
    "        return band.log10().multiply(10)\n",
    "    \n",
    "    def mtDespeck(images, radius, units):\n",
    "        def mapMeanSpace(image):\n",
    "            reducer = ee.Reducer.mean()\n",
    "            kernel = ee.Kernel.square(radius, units)\n",
    "            mean = image.reduceNeighborhood(reducer, kernel).rename(meanBand)\n",
    "            ratio = image.divide(mean).rename(ratioBand)\n",
    "            return image.addBands(mean).addBands(ratio).copyProperties(image)\n",
    "        \n",
    "        bands     = images.first().bandNames()\n",
    "        \n",
    "        def cat_mean(bandName):\n",
    "            return ee.String(bandName).cat('_mean')\n",
    "        def cat_ratio(bandName):\n",
    "            return ee.String(bandName).cat('_ratio')\n",
    "        \n",
    "        meanBand  = bands.map(cat_mean)\n",
    "        ratioBand = bands.map(cat_ratio)\n",
    "    \n",
    "        # compute spatial average for all images\n",
    "        meanSpace = images.map(mapMeanSpace)\n",
    "    \n",
    "        def mtDespeckSingle(image):\n",
    "            angle      = image.select('angle')\n",
    "            meanSpace2 = ee.ImageCollection(meanSpace).select(ratioBand)\n",
    "            b = image.select(meanBand)\n",
    "            return (b.multiply(meanSpace2.sum()).divide(meanSpace2.count()).rename(bands)).copyProperties(image).set('system:time_start', image.get('system:time_start'))\n",
    "        \n",
    "        return meanSpace.map(mtDespeckSingle)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.9"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
