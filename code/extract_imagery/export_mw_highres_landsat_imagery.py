""" to run this script, open the command prompt, type:
#Create a google earth engine acocunt,  then follow the google earth engine instructions to first create an appropriate python environment for extraction (ee)
conda activate ee
#enter the filepath of this file on your system below
python ".../export_mw_highres_imagery.py"
"""

import ee
ee.Initialize()

def cloudMaskL457(image): 
  qa = image.select('pixel_qa')
  cloud = qa.bitwiseAnd(1 << 5).And(qa.bitwiseAnd(1 << 7)).Or(qa.bitwiseAnd(1 << 3))
  mask2 = image.mask().reduce(ee.Reducer.min())
  return(image.updateMask(cloud.Not()).updateMask(mask2))

def cloudmask(image): 
  clear = ee.Algorithms.Landsat.simpleCloudScore(image).select(['cloud']).lte(20)
  return(image.updateMask(clear))


mw = ee.Geometry.Rectangle(-91.37635548114778, 29.325054203049273, -72.34803516864778, 42.31009875176506)

toa0 = ee.ImageCollection("LANDSAT/LE07/C01/T1_TOA").map(cloudmask).filterDate(ee.DateRange('2000-05-01', '2000-08-30')).median().select(['B3','B2','B1','B8'],['red_0','green_0','blue_0','B8_0'])
hsv0 = toa0.select(['red_0', 'green_0', 'blue_0']).rgbToHsv()
sharpened0 = ee.Image.cat([hsv0.select('hue'), hsv0.select('saturation'), toa0.select('B8_0')]).hsvToRgb().select(['red','green','blue'],['psred_0','psgreen_0','psblue_0'])
toa10 = ee.ImageCollection("LANDSAT/LE07/C01/T1_TOA").map(cloudmask).filterDate(ee.DateRange('2010-05-01', '2010-08-30')).median().select(['B3','B2','B1','B8'],['red_10','green_10','blue_10','B8_10'])
hsv10 = toa10.select(['red_10', 'green_10', 'blue_10']).rgbToHsv()
sharpened10 = ee.Image.cat([hsv10.select('hue'), hsv10.select('saturation'), toa10.select('B8_10')]).hsvToRgb().select(['red','green','blue'],['psred_10','psgreen_10','psblue_10'])
toa15 = ee.ImageCollection("LANDSAT/LE07/C01/T1_TOA").map(cloudmask).filterDate(ee.DateRange('2015-05-01', '2015-08-30')).median().select(['B3','B2','B1','B8'],['red_15','green_15','blue_15','B8_15'])
hsv15 = toa15.select(['red_15', 'green_15', 'blue_15']).rgbToHsv()
sharpened15 = ee.Image.cat([hsv15.select('hue'), hsv15.select('saturation'), toa15.select('B8_15')]).hsvToRgb().select(['red','green','blue'],['psred_15','psgreen_15','psblue_15'])

ls0 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2000-05-01', '2000-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_0','green_0','blue_0','B4_0','B5_0','B6_0','B7_0'])
ls10 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2010-05-01', '2010-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_10','green_10','blue_10','B4_10','B5_10','B6_10','B7_10'])
ls15 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2015-05-01', '2015-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_15','green_15','blue_15','B4_15','B5_15','B6_15','B7_15']) 


urban = ee.Image("users/armanucsd/national_bg_urban_buffer1mile").select(['first'], ['urban'])

allbands =  ls0.addBands(ls10).addBands(ls15).addBands(ee.Image.pixelLonLat()).addBands(urban).addBands(sharpened0).addBands(sharpened10).addBands(sharpened15)


blobs = ee.FeatureCollection("users/armanucsd/popdbuff_splitblobs_national")
mwblobs = blobs.filterBounds(mw)


def outfeat(fnum):
  fnumstr=str(fnum)
  descrip = 'blobs_papi_highres' + fnumstr
  geo = ee.Feature(mwblobs.filterMetadata('fnum', 'equals', fnumstr).first()).geometry()
  
  tfr_opts = {}
  tfr_opts['patchDimensions'] = [96,96]
  tfr_opts['kernelSize'] = [12,12]

  
  task=ee.batch.Export.image.toDrive(
    folder='TFR_p96k12_mwblobs_papi_highres',
    image=allbands.float(),  
    description=descrip,
    scale=15,
    region=geo,
    maxPixels=70e6, 
    fileFormat='TFRecord',
    formatOptions=tfr_opts
  )

  task.start()


##3000,4786
##1000,3000 
##0,1000

for i in range(0,1000):
  outfeat(i)


