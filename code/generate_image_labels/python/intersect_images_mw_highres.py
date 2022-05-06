""" to run this script, open the command prompt enter the below line (note python environment here needs to be pre-loaded with argis pro package and licenses):
python "code\generate image labels\python\intersect_images_mw_highres.py"
"""

import arcpy
from multiprocessing import Pool, TimeoutError
import time
import os
from os import path
t0 = time.clock()

#num_proc=2
num_proc=4

arcpy.env.qualifiedFieldNames = False
arcpy.env.overwriteOutput = True


arcpy.env.workspace = r"[enter gdb name].gdb"
arcpy.env.overwriteOutput = True

#all
states = ["DC","AL","AZ","AR","CA","CO","CT","DE","FL","GA","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"]


def f(state):
        
        try:                        
                arcpy.MakeFeatureLayer_management(r"data\labels\source files\block_shapefiles\{}_block_2010.shp".format(state), "shapes10{}".format(state))

                for i in range(0,37):
                        arcpy.TabulateIntersection_analysis("squares_byimg_national_mw_highres{}".format(i), "img_id", "shapes10{}".format(state), r"data\labels\generated files\image_intersections\int10_{}_national_mw_highres{}.csv".format(state, i), "GISJOIN")

                print("{} Done".format(state))

        except:
                print("{} Failed".format(state))


        
if __name__ == '__main__':
	pool =Pool(processes=num_proc)
	print(pool.map(f,states))



t1 = time.clock()
print(t1-t0)

