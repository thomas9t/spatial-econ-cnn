

clear
clear matrix
clear mata
set more off
set scheme s1color
estimates clear
graph drop _all
set matsize 11000
log close _all
file close _all
set maxvar 20000


cd "...set base working directory here..."


*remove images which google earth engine exported with overlap
do "code\generate_image_labels\drop_redundant_images_national.do"

//these codes compute the area of spatial intersections between census blocks and our exported images
*in code\generate_image_labels\python, run (in the following order):
*1) make_image_shapes_large.py, make_image_shapes_small.py, make_image_shapes_mw_highres.py
*2) intersect_images_large.py, intersect_images_small.py, intersect_images_mw_highres.py
*3) assign_images_to_blobs.py

*clean block-level Census labels
do "code\generate_image_labels\cleaning_block_labels.do"

*combine the output of the python code (image intersections with blocks) and block-level census labels to interpolate image-level census labels
do "code\generate_image_labels\label_images_blockcw.do"


