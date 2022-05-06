
clear
clear matrix
set more off
set scheme s1color
estimates clear
graph drop _all
set matsize 11000
log close _all
file close _all
clear mata
set maxvar 20000

set seed 41205837

//cleaned image level predictions panel for use in applications

use data/predictions/preds_large_national_clean, clear

drop *base* *_nl* *_RGB* sample *15* area image_coverage urban groupshare_0 subset_outsamp rand_outsamp random_blob* county state popshare_0 white_0 black_0 hispanic_0 workage_0 female_0 emp_* fnum subset 
order img_id lat lng inc_*_feature_oos dinc_*_feature_oos pop_*_feature_oos dpop_*_feature_oos inc_*_oos dinc_*_oos pop_*_oos dpop_*_oos true_* 
rename *_oos* **
desc

save data/applications/application_predictions_large, replace



//geographic crosswalk from images to 2010 census blocks
preserve
use data/labels/generated_files/block_labels_cw_wrevisions_wblockinc, clear
keep gisjoin block_area
tempfile block_areas
save `block_areas'
restore

merge 1:m img_id using data/labels/generated_files/image_intersections/int_merged_large, assert(3 2) keep(3) nogen

keep gisjoin img_id inc_* pop_* area

sort img_id
by img_id: egen img_area = total(area)
gen share_of_img = area/img_area


keep gisjoin inc* pop* share_of_img

//weighting population and income counts by spatial overlap
foreach v of varlist inc* pop* {
	replace `v' = exp(`v')*share_of_img
}

//summing up by block
collapse (sum) inc* pop*, by(gisjoin)

//returning to log values
foreach v of varlist inc* pop* {
	replace `v' = log(`v')
}

save data/applications/application_predictions_blocks, replace



