""" to run this script, open the command prompt, type:
#Create a google earth engine acocunt,  then follow the google earth engine instructions to first create an appropriate python environment for extraction (ee)
conda activate ee
#enter the filepath of this file on your system below
python ".../export_nightlights_blocks.py"
"""

import ee
ee.Initialize()

blocks = ee.FeatureCollection("TIGER/2010/Blocks")

dmsp00 = ee.Image('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F142000').select('avg_vis')
dmsp10 = ee.Image('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F182010').select('avg_vis')

states = ['01', '04', '05', '08', '09', '10', '11', '12', '13', '19', '16', '17', '18', '20', '21', '22', '25', '24', '23', '26', '27', '29', '28', '30', '37', '38', '31', '33', '34', '35', '32', '36', '39', '40', '41', '42', '44', '45', '46', '47', '49', '51', '50', '53', '55', '54', '56']

sol = function(state,split){
  
  if (split === undefined || split === null){var split = 0}

      desc00 = ee.String('dmps10rawsum00_blocks_').cat(state).cat(split.toString()).cat('of5')
      descrip00 = desc00.getInfo()

      desc10 = ee.String('dmps10rawsum10_blocks_').cat(state).cat(split.toString()).cat('of5')
      descrip10 = desc10.getInfo()

  if (split==0) filtered_blocks = blocks.filter(ee.Filter.eq('statefp10',state))
  
  if (split==-1) filtered_blocks = blocks.filter(ee.Filter.and(ee.Filter.eq('statefp10',state),ee.Filter.lte('pop10',1)))

  if (split==1) filtered_blocks = blocks.filter(ee.Filter.and(ee.Filter.eq('statefp10',state),ee.Filter.gt('pop10',1),ee.Filter.lte('pop10',3))) 

  if (split==2) filtered_blocks = blocks.filter(ee.Filter.and(ee.Filter.eq('statefp10',state),ee.Filter.gt('pop10',3),ee.Filter.lte('pop10',10))) 
  if (split==3) filtered_blocks = blocks.filter(ee.Filter.and(ee.Filter.eq('statefp10',state),ee.Filter.gt('pop10',10),ee.Filter.lte('pop10',50))) 
  if (split==4) filtered_blocks = blocks.filter(ee.Filter.and(ee.Filter.eq('statefp10',state),ee.Filter.gt('pop10',50),ee.Filter.lte('pop10',100))) 
  if (split==5) filtered_blocks = blocks.filter(ee.Filter.and(ee.Filter.eq('statefp10',state),ee.Filter.gt('pop10',100)))
  

  stats00 = dmsp00.reduceRegions({
    reducer: ee.Reducer.sum(),
    collection: filtered_blocks,
    scale: dmsp00.projection().nominalScale(),
    tileScale: 2
  })

  stats10 = dmsp10.reduceRegions({
    reducer: ee.Reducer.sum(),
    collection: filtered_blocks,
    scale: dmsp10.projection().nominalScale(),
    tileScale: 2
  })
  
  sol_out00 = ee.FeatureCollection(stats00)
  sol_out10 = ee.FeatureCollection(stats10)

  Export.table.toDrive({
    collection: sol_out00,
    description: descrip00,
    folder: 'extract_imagery',
    fileFormat: 'CSV'
    })
  
  Export.table.toDrive({
    collection: sol_out10,
    description: descrip10,
    folder: 'extract_imagery',
    fileFormat: 'CSV'
    })

}



#for 2000
bigstates00 = ['06','23','41','48']

#for 2010
bigstates10 = ['06','12','48']


sol_split = function(state){
  sol(state,-1);
  sol(state,1);
  sol(state,2);
  sol(state,3);
  sol(state,4);
  sol(state,5);
}  

bigstates.map(sol_split)


