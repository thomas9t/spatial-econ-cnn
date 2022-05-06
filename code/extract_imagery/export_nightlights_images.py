""" to run this script, open the command prompt, type:
#Create a google earth engine acocunt,  then follow the google earth engine instructions to first create an appropriate python environment for extraction (ee)
conda activate ee
#enter the filepath of this file on your system below
python ".../export_nightlights_images.py"
"""

import ee
ee.Initialize()


dmsp00 = ee.Image('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F142000').select('avg_vis')
dmsp10 = ee.Image('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F182010').select('avg_vis')


large_image_squares = ee.FeatureCollection('users/armanucsd/dmsp_squares_large')
small_image_squares = ee.FeatureCollection('users/armanucsd/dmsp_squares_small')


large_stats10 = dmsp10.reduceRegions({
    reducer: ee.Reducer.sum(),
    collection: large_image_squares,
    scale: dmsp10.projection().nominalScale(),
    tileScale: 2
})

large_stats00 = dmsp00.reduceRegions({
    reducer: ee.Reducer.sum(),
    collection: large_image_squares,
    scale: dmsp00.projection().nominalScale(),
    tileScale: 2
})

small_stats10 = dmsp10.reduceRegions({
    reducer: ee.Reducer.sum(),
    collection: small_image_squares,
    scale: dmsp10.projection().nominalScale(),
    tileScale: 2
})

small_stats00 = dmsp00.reduceRegions({
    reducer: ee.Reducer.sum(),
    collection: small_image_squares,
    scale: dmsp00.projection().nominalScale(),
    tileScale: 2
})
 

 
large_sol_out_00 = ee.FeatureCollection(large_stats00)
large_sol_out_10 = ee.FeatureCollection(large_stats10)
small_sol_out_00 = ee.FeatureCollection(small_stats00)
small_sol_out_10 = ee.FeatureCollection(small_stats10)

Export.table.toDrive({
    collection: large_sol_out_00,
    description: "dmsprawsum_largeimgs_00",
    folder: 'extract_imagery',
    fileFormat: 'CSV'
})

Export.table.toDrive({
    collection: large_sol_out_10,
    description: "dmsprawsum_largeimgs_10",
    folder: 'extract_imagery',
    fileFormat: 'CSV'
})

Export.table.toDrive({
    collection: small_sol_out_00,
    description: "dmsprawsum_smallimgs_00",
    folder: 'extract_imagery',
    fileFormat: 'CSV'
})

Export.table.toDrive({
    collection: small_sol_out_10,
    description: "dmsprawsum_smallimgs_10",
    folder: 'extract_imagery',
    fileFormat: 'CSV'
})
