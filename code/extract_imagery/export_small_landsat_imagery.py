""" to run this script, open the command prompt, type:
#Create a google earth engine acocunt,  then follow the google earth engine instructions to first create an appropriate python environment for extraction (ee)
conda activate ee
#enter the filepath of this file on your system below
python ".../export_small_landsat_imagery.py"
"""

import ee
ee.Initialize()

def cloudMaskL457(image): 
  qa = image.select('pixel_qa')
  cloud = qa.bitwiseAnd(1 << 5).And(qa.bitwiseAnd(1 << 7)).Or(qa.bitwiseAnd(1 << 3))
  mask2 = image.mask().reduce(ee.Reducer.min())
  return(image.updateMask(cloud.Not()).updateMask(mask2))



ls0 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2000-05-01', '2000-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_0','green_0','blue_0','B4_0','B5_0','B6_0','B7_0']) 
ls1 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2001-05-01', '2001-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_1','green_1','blue_1','B4_1','B5_1','B6_1','B7_1']) 
ls2 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2002-05-01', '2002-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_2','green_2','blue_2','B4_2','B5_2','B6_2','B7_2']) 
ls3 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2003-05-01', '2003-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_3','green_3','blue_3','B4_3','B5_3','B6_3','B7_3']) 
ls4 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2004-05-01', '2004-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_4','green_4','blue_4','B4_4','B5_4','B6_4','B7_4']) 
ls5 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2005-05-01', '2005-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_5','green_5','blue_5','B4_5','B5_5','B6_5','B7_5']) 
ls6 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2006-05-01', '2006-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_6','green_6','blue_6','B4_6','B5_6','B6_6','B7_6']) 
ls7 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2007-05-01', '2007-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_7','green_7','blue_7','B4_7','B5_7','B6_7','B7_7']) 
ls8 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2008-05-01', '2008-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_8','green_8','blue_8','B4_8','B5_8','B6_8','B7_8']) 
ls9 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2009-05-01', '2009-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_9','green_9','blue_9','B4_9','B5_9','B6_9','B7_9'])
ls10 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2010-05-01', '2010-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_10','green_10','blue_10','B4_10','B5_10','B6_10','B7_10']) 
ls11 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2011-05-01', '2011-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_11','green_11','blue_11','B4_11','B5_11','B6_11','B7_11']) 
ls12 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2012-05-01', '2012-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_12','green_12','blue_12','B4_12','B5_12','B6_12','B7_12']) 
ls13 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2013-05-01', '2013-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_13','green_13','blue_13','B4_13','B5_13','B6_13','B7_13']) 
ls14 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2014-05-01', '2014-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_14','green_14','blue_14','B4_14','B5_14','B6_14','B7_14']) 
ls15 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2015-05-01', '2015-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_15','green_15','blue_15','B4_15','B5_15','B6_15','B7_15']) 
ls16 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2016-05-01', '2016-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_16','green_16','blue_16','B4_16','B5_16','B6_16','B7_16']) 
ls17 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2017-05-01', '2017-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_17','green_17','blue_17','B4_17','B5_17','B6_17','B7_17']) 
ls18 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2018-05-01', '2018-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_18','green_18','blue_18','B4_18','B5_18','B6_18','B7_18']) 
ls19 = ee.ImageCollection("LANDSAT/LE07/C01/T1_SR").filterDate(ee.DateRange('2019-05-01', '2019-08-30')).map(cloudMaskL457).median().select(['B3','B2','B1','B4','B5','B6','B7'],['red_19','green_19','blue_19','B4_19','B5_19','B6_19','B7_19'])


dmsp_bluhm00 = ee.Image('users/armanucsd/F142000_Corrected').select(['b1'],['nl_bluhm_0'])
dmsp_bluhm10 = ee.Image('users/armanucsd/F182010_Corrected').select(['b1'],['nl_bluhm_10'])

dmsp_cal00 = ee.Image('NOAA/DMSP-OLS/CALIBRATED_LIGHTS_V4/F12-F15_20000103-20001229_V4').select(['avg_vis'],['nl_cal_0'])
dmsp_cal10 = ee.Image('NOAA/DMSP-OLS/CALIBRATED_LIGHTS_V4/F16_20100111-20101209_V4').select(['avg_vis'],['nl_cal_10'])

dmsp_00 = ee.Image('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F152000').select(['avg_vis'],['nl_0'])
dmsp_01 = ee.Image('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F152001').select(['avg_vis'],['nl_1'])
dmsp_02 = ee.Image('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F152002').select(['avg_vis'],['nl_2'])
dmsp_03 = ee.Image('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F152003').select(['avg_vis'],['nl_3'])
dmsp_04 = ee.Image('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F152004').select(['avg_vis'],['nl_4'])
dmsp_05 = ee.Image('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F152005').select(['avg_vis'],['nl_5'])
dmsp_06 = ee.Image('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F152006').select(['avg_vis'],['nl_6'])
dmsp_07 = ee.Image('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F152007').select(['avg_vis'],['nl_7'])
dmsp_08 = ee.Image('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F152008').select(['avg_vis'],['nl_8'])
dmsp_09 = ee.Image('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F162009').select(['avg_vis'],['nl_9'])
dmsp_10 = ee.Image('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F182010').select(['avg_vis'],['nl_10'])
dmsp_11 = ee.Image('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F182011').select(['avg_vis'],['nl_11'])
dmsp_12 = ee.Image('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F182012').select(['avg_vis'],['nl_12'])
dmsp_13 = ee.Image('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F182013').select(['avg_vis'],['nl_13'])

viirs_14 = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG').filter(ee.Filter.date('2014-01-01', '2015-01-01')).select(['avg_rad'],['nl_14']).median()
viirs_15 = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG').filter(ee.Filter.date('2015-01-01', '2016-01-01')).select(['avg_rad'],['nl_15']).median()
viirs_16 = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG').filter(ee.Filter.date('2016-01-01', '2017-01-01')).select(['avg_rad'],['nl_16']).median()
viirs_17 = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG').filter(ee.Filter.date('2017-01-01', '2018-01-01')).select(['avg_rad'],['nl_17']).median()
viirs_18 = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG').filter(ee.Filter.date('2018-01-01', '2019-01-01')).select(['avg_rad'],['nl_18']).median()
viirs_19 = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG').filter(ee.Filter.date('2019-01-01', '2020-01-01')).select(['avg_rad'],['nl_19']).median()

nlcd_00= ee.Image("USGS/NLCD/NLCD2001").select(['landcover'],['lc_0'])
nlcd_10= ee.Image("USGS/NLCD/NLCD2011").select(['landcover'],['lc_10'])
nlcd_16= ee.Image("USGS/NLCD/NLCD2016").select(['landcover'],['lc_16'])

urban = ee.Image("users/armanucsd/national_bg_urban_buffer1mile").select(['first'], ['urban'])


allbands =  ls0.addBands(ls1).addBands(ls2).addBands(ls3).addBands(ls4).addBands(ls5).addBands(ls6).addBands(ls7).addBands(ls8).addBands(ls9).addBands(ls10).addBands(ls11).addBands(ls12).addBands(ls13).addBands(ls14).addBands(ls15).addBands(ls16).addBands(ls17).addBands(ls18).addBands(ls19).addBands(ee.Image.pixelLonLat()).addBands(urban).addBands(ee.Image.pixelLonLat()).addBands(urban).addBands(dmsp_bluhm00).addBands(dmsp_bluhm10).addBands(dmsp_cal00).addBands(dmsp_cal10).addBands(dmsp_00).addBands(dmsp_01).addBands(dmsp_02).addBands(dmsp_03).addBands(dmsp_04).addBands(dmsp_05).addBands(dmsp_06).addBands(dmsp_07).addBands(dmsp_08).addBands(dmsp_09).addBands(dmsp_10).addBands(dmsp_11).addBands(dmsp_12).addBands(dmsp_13).addBands(viirs_14).addBands(viirs_15).addBands(viirs_16).addBands(viirs_17).addBands(viirs_18).addBands(viirs_19).addBands(nlcd_00).addBands(nlcd_10).addBands(nlcd_16)

blobs = ee.FeatureCollection("users/armanucsd/popdbuff_splitblobs_national")

def outfeat(fnum):
  fnumstr=str(fnum)
  descrip = 'blobs_papi_national_small' + fnumstr
  geo = ee.Feature(blobs.filterMetadata('fnum', 'equals', fnumstr).first()).geometry()
  
  tfr_opts = {}
  tfr_opts['patchDimensions'] = [48,48]
  tfr_opts['kernelSize'] = [6,6]

  
  task=ee.batch.Export.image.toDrive(
    folder='TFR_sr_p48k6_prediction_blobs_papi_national_coder_getall',
    image=allbands.float(),  
    description=descrip,
    scale=30,
    region=geo,
    maxPixels=70e6, 
    fileFormat='TFRecord',
    formatOptions=tfr_opts
  )

  task.start()



#0 to 4785

#run 1: 0, 1500
#run 2: 1500, 3000
#run 3: 3000, 4000
#run 4: 4000, 4786
for i in range(3000,4787):
  outfeat(i)


