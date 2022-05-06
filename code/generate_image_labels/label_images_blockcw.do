
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

*number of files in each image set
local sizelarge = 28
local sizesmall = 76
local sizemw_highres = 36

foreach size in large small mw_highres {
	//this section is commented out because the intermediate int10_[state]_national_[size][count] csv files of computed geographic overlaps between images and 2010 census blocks are not included in this repository, to conserve space. To replicate this stage you would need to run the python script code\generate_image_labels\python\intersect_images_[size].py in this repository.
	/*
	local states DC AL AZ AR CA CO CT DE FL GA ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY

	quietly {
	foreach st in `states' {
	noisily di "Starting State `st'"
		forval i = 0/`size`size'' {
			
			import delimited using data\labels\generated_files\image_intersections\int10_`st'_national_`size'`i'.csv, clear

			if _N>0 {
				keep img_id gisjoin percentage area
				rename percentage pct
				replace pct = pct/100
				capture append using `ints'
				if _rc!=0 tempfile ints
				save `ints', replace
			}
		}
	}
	use `ints', clear
	noisily save data\labels\generated_files\image_intersections\int_merged_`size', replace
	}
	*/


	use data\labels\generated_files\image_intersections\int_merged_`size', clear


	merge m:1 gisjoin using data\labels\generated_files\block_labels_cw, nogen keep(match)

	local bvars "pop_00 pop_10 pop_20 inc_00 inc_10 inc_7 inc_15 inc_17 white_00 black_00 hispanic_00 workage_00 female_00 groupshare_00 emp_sec* emp_bus_serv_00 emp_nonbus_serv_00 emp_prod_00"
	local bgvars "pop_bg_* inc_bg_* "
	local cntyvars "pop_cnty* inc_cnty* emp*_cnty_*"

	//getting portion of population and total income counts in overlap region
	foreach v of varlist `bvars' {
		replace `v' = `v'*(area/block_area)
	}

	//getting spatially averaged containing bg and county-level initial conditions
	gen gisjoin_cnty = substr(gisjoin_bg,1,8)
	//this cnty_areas file is a created in cleaning_block_labels.do
	merge m:1 gisjoin_cnty using data\labels\source_files\cnty_areas, nogen keep(match)
	
	foreach v of varlist emp*_cnty* {
		replace `v' = `v'*pop_cnty_00
	}

	//shares of image in intersection
	bysort img_id: egen totpct = total(pct)
	replace pct = pct/totpct
	foreach v of varlist popshare `bgvars' `cntyvars' {
		replace `v' = `v'*pct
	}

	//generating county and state
	gen county = substr(gisjoin_bg,1,8)
	gen state = substr(gisjoin_bg,2,2)
	bysort img_id: egen maxpct = max(pct)
	replace county = "" if pct!=maxpct
	replace state = "" if pct!=maxpct

	collapse (sum) area pct popshare `bvars' `bgvars' `cntyvars' (firstnm) county state , by(img_id)

	//divide the count by demographic by the population in the image (based on relevant source level of aggregation)
	foreach v of varlist white_00 black_00 hispanic_00 workage_00 female_00 groupshare_00 emp_sec* emp_bus_serv_00 emp_nonbus_serv_00 emp_prod_00 {
		replace `v' = `v'/pop_00
	}
	foreach v of varlist emp_bus_serv_cnty_00 emp_nonbus_serv_cnty_00 emp_prod_cnty_00  {
		replace `v' = `v'/pop_cnty_00
	}	

	rename pct image_coverage
	
	//this file is generated in drop_redundant_images_national.do
	merge 1:1 img_id using data\labels\generated_files\valid_imgs_rowcoltrim_`size'_addon, nogen keep(3)

	foreach v of varlist pop_* inc_* {
		gen log_`v' = log(`v')
		drop `v'
	}


	duplicates drop lat lng, force
			
	// Bringing in blob assignment and generating data subset
	preserve 
	//this file is generated in assign_images_to_blobs.py
	import delimited using data\labels\generated_files\image_intersections\blob_ints_`size'.csv, clear
	drop *objectid* percentage pnt_count
	//removing images right on border between blobs
	duplicates tag img_id, gen(dups)
	drop if dups>0
	drop dups
	tempfile blob_ints
	save `blob_ints'
	restore


	merge 1:1 img_id using `blob_ints', nogen keep(match)



	//generating subset assignment
	preserve
	collapse (firstnm) img_id , by(fnum)
	gen random_blob_order = runiform()
	gen subset = "train" if random_blob_order<0.5
	replace subset = "validation" if random_blob_order<0.7 & subset==""
	replace subset = "test" if subset==""
	drop img_id
	tab subset
	tempfile assign
	save `assign'
	restore

	merge m:1 fnum using `assign', nogen assert(match)

	tab subset

	gen sample = groupshare<.05 & popshare<.85 & urban>=.9
	//tab subset if sample==1

	capture drop filename img_num_in_file

	destring state, replace

	order img_id lat lng fnum subset random_blob_order popshare urban log*
	save data\labels\generated_files\blockcw_labelled_imgs_`size', replace

	export delimited using data\labels\generated_files\blockcw_labelled_imgs_`size'.csv, replace

	if "`size'"=="large" {
		//for subsets map
		collapse (firstnm) subset, by(fnum)
		export delimited using data\labels\generated_files\blob_assignment_`size'_blockcw.csv, replace
	}

}




