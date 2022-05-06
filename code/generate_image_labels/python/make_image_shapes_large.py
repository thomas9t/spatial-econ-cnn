""" to run this script, open the command prompt enter the below line (note python environment here needs to be pre-loaded with argis pro package and licenses):
python "code\generate image labels\python\make_image_shapes_large.py"
"""

import arcpy
import math

arcpy.env.qualifiedFieldNames = False
arcpy.env.overwriteOutput = True

#Need to set up an arcGIS pro geodatabase to run these computations in
arcpy.env.workspace = r"[enter gdb name].gdb"
arcpy.env.overwriteOutput = True


#make national squares
arcpy.management.XYTableToPoint(r"data\labels\source files\allpredpts_natinoal_large_addon.csv", "image_pts_national_large","lng", "lat")

arcpy.Buffer_analysis("image_pts_national_large", "circles_byimg_national_large", "1200 Meters")
arcpy.MinimumBoundingGeometry_management("circles_byimg_national_large","squares_byimg_national_large")


#The rest of this script breaks up the national file of image boundaries (i.e. squares_byimg_national_large) into separate files of approximately 10 thousand images each, to facilitate streamlined parallel computation across images
splits = 29
max = 283841

interval = math.ceil(max/splits)

for i in range(0, splits):
     
    low = -1 + (interval*i)
    high = interval + (interval*i) -1
    if i == splits-1 : high = max

    #break squares up into 10k chunks
    arcpy.FeatureClassToFeatureClass_conversion ("squares_byimg_national_large",r"[enter gdb name].gdb","squares_byimg_national_large{}".format(i),'"OBJECTID" > {} AND "OBJECTID" <= {}'.format(low, high))

    #break pts up into 10k chunks
    arcpy.FeatureClassToFeatureClass_conversion ("image_pts_national_large",r"[enter gdb name].gdb","pts_byimg_national_large{}".format(i),'"OBJECTID" > {} AND "OBJECTID" <= {}'.format(low, high))





