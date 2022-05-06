""" to run this script, open the command prompt enter the below line (note python environment here needs to be pre-loaded with argis pro package and licenses):
python "code\generate image labels\python\make_image_shapes_mw_highres.py"
"""

import arcpy
import math

arcpy.env.qualifiedFieldNames = False
arcpy.env.overwriteOutput = True

#Need to set up an arcGIS pro geodatabase to run these computations in
arcpy.env.workspace = r"[enter gdb name].gdb"
arcpy.env.overwriteOutput = True


#make national squares
arcpy.management.XYTableToPoint(r"data\labels\source files\allpredpts_mw_highres_addon.csv", "image_pts_national_mw_highres","lng", "lat")

arcpy.Buffer_analysis("image_pts_national_mw_highres", "circles_byimg_national_mw_highres", "720 Meters")
arcpy.MinimumBoundingGeometry_management("circles_byimg_national_mw_highres","squares_byimg_national_mw_highres")


splits = 37
max =  363035

interval = math.ceil(max/splits)

for i in range(0, splits):
     
    low = -1 + (interval*i)
    high = interval + (interval*i) -1
    if i == splits-1 : high = max

    #break squares up into 10k chunks
    arcpy.FeatureClassToFeatureClass_conversion ("squares_byimg_national_mw_highres",r"[enter gdb name].gdb","squares_byimg_national_mw_highres{}".format(i),'"OBJECTID" > {} AND "OBJECTID" <= {}'.format(low, high))

    #break pts up into 10k chunks
    arcpy.FeatureClassToFeatureClass_conversion ("image_pts_national_mw_highres",r"[enter gdb name].gdb","pts_byimg_national_mw_highres{}".format(i),'"OBJECTID" > {} AND "OBJECTID" <= {}'.format(low, high))





