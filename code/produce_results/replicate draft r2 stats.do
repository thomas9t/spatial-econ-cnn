
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

// merging together all of the CNN model prediction files
*extent of sample (mw is the mid-atlantic region)
foreach r in national mw {
	*image sizes
	foreach s in large small {
	
		local i = 0	

		*predicting differences or levels
		foreach p in diff level {

			*spectral bands included
			foreach m in base RGB nl { 
				*income and population outcomes
				foreach o in inc pop inc_pop {
					*whether initial conditions are used in the predictions
					foreach f in "_feature" "_feature_high" "_high" "" {
						
						di "block_`s'_`r'_`p'_`m'`f'_`o'_predictions"
						capture confirm file data/predictions/`p'/block_`s'_`r'_`p'_`m'`f'_`o'_predictions.csv
						if _rc==0 {
						local i = `i'+1
						import delimited using data/predictions/`p'/block_`s'_`r'_`p'_`m'`f'_`o'_predictions.csv, clear
						count
						
						order img_id
						
						if "`p'"=="diff" {
							rename v1 d`o'_010_`m'`f'
							capture rename v2 d`o'_015_`m'`f'
							capture rename v3 d`o'_1015_`m'`f'
						}
						if "`p'"=="level" {
							rename v1 `o'_0_`m'`f'
							rename v2 `o'_10_`m'`f'
							capture rename v3 `o'_15_`m'`f'
						}
						
						if `i'==1 tempfile preds_`s'_`r'
						else merge 1:1 img_id using `preds_`s'_`r'', assert(3) nogen
						save `preds_`s'_`r'', replace
						
						}
						
					}
				}
			}
		}
		
	save data\predictions\preds_`s'_`r', replace
	}
}


//Out-of-period model

local large_oop_files "large_feature_all_years_predictions_trained_on_all_images large_all_years_predictions_trained_on_all_images large_diff_pop_feature_10_year_predictions_trained_on_all_images large_diff_inc_10_year_predictions_trained_on_all_images large_diff_inc_feature_10_year_predictions_trained_on_all_images large_diff_pop_10_year_predictions_trained_on_all_images large_diff_inc_feature_17_year_predictions_trained_on_all_images large_diff_inc_17_year_predictions_trained_on_all_images large_diff_pop_19_year_predictions_trained_on_all_images large_diff_pop_feature_19_year_predictions_trained_on_all_images"
local small_oop_files "small_feature_all_years_predictions_trained_on_all_images small_all_years_predictions_trained_on_all_images  small_diff_inc_feature_10_year_predictions_trained_on_all_images small_diff_inc_10_year_predictions_trained_on_all_images small_diff_pop_10_year_predictions_trained_on_all_images small_diff_pop_feature_10_year_predictions_trained_on_all_images"

foreach s in large small {
	local i = 0
	foreach d in ``s'_oop_files' {
		local i = `i'+1
		local f ""
		if strmatch("`d'","*_feature_*") local f = "_feature" 

		import delimited using data/predictions/out_of_period_model/`d'.csv, clear
		
		//dropping variables that are empty
		foreach v of varlist * {
			quietly count if `v' == .
			if r(N)==_N drop `v' 
		}
		
		rename * *`f'_oos
		if `i'>2 rename * d*
		rename *img_id* img_id
		
		if `i'==1 tempfile preds_`s'
		else merge 1:1 img_id using `preds_`s'', nogen
		save `preds_`s'', replace
		
	}	
	
	merge 1:1 img_id using data/predictions/preds_`s'_national, nogen
	save data/predictions/preds_`s'_national, replace
}




// cleaning merged prediction files
*
use data/predictions/preds_large_national, clear
														   
merge 1:1 img_id using "data/labels/generated_files/blockcw_labelled_imgs_national_large", assert(2 3) keep(3) nogen

gen true_dinc_0_10 = log_inc_10-log_inc_00
gen true_dpop_0_10 = log_pop_10-log_pop_00
gen true_dinc_0_15 = log_inc_15-log_inc_00
gen true_dinc_10_15 = log_inc_15-log_inc_10
gen true_dinc_7_17 = log_inc_17 - log_inc_7
gen true_dinc_0_17 = log_inc_17 - log_inc_00
gen true_dpop_10_20 = log_pop_20 - log_pop_10
gen true_dpop_0_20 = log_pop_20 - log_pop_00

rename log_pop* true_pop*
rename log_inc* true_inc*
rename *_00 *_0

gen true_inc_pop_0 = log(exp(true_inc_0)/exp(true_pop_0))
gen true_inc_pop_10 = log(exp(true_inc_10)/exp(true_pop_10))
gen true_dinc_pop_0_10 = true_inc_pop_10 - true_inc_pop_0



replace subset = "(1) train" if subset=="train"
replace subset = "(2) validation" if subset=="validation"
replace subset = "(3) test" if subset=="test"

save data/predictions/preds_large_national_clean, replace


use data/predictions/preds_small_national, clear

merge 1:1 img_id using data/labels/generated_files/blockcw_labelled_imgs_national_small, assert(2 3) keep(3) nogen

gen true_dinc_0_10 = log_inc_10-log_inc_00
gen true_dpop_0_10 = log_pop_10-log_pop_00

rename log_pop_00 true_pop_0
rename log_pop_10 true_pop_10
rename log_inc_00 true_inc_0
rename log_inc_10 true_inc_10

gen true_inc_pop_0 = log(exp(true_inc_0)/exp(true_pop_0))
gen true_inc_pop_10 = log(exp(true_inc_10)/exp(true_pop_10))
gen true_dinc_pop_0_10 = true_inc_pop_10 - true_inc_pop_0

replace subset = "(1) train" if subset=="train"
replace subset = "(2) validation" if subset=="validation"
replace subset = "(3) test" if subset=="test"

save data/predictions/preds_small_national_clean, replace


use data/predictions/preds_small_mw, clear

merge 1:1 img_id using data/labels/generated_files/blockcw_labelled_imgs_mw_highres, assert(2 3) keep(3) nogen

gen true_dinc_0_10 = log_inc_10-log_inc_00
gen true_dpop_0_10 = log_pop_10-log_pop_00

rename log_pop_00 true_pop_0
rename log_pop_10 true_pop_10
rename log_inc_00 true_inc_0
rename log_inc_10 true_inc_10

replace subset = "(1) train" if subset=="train"
replace subset = "(2) validation" if subset=="validation"
replace subset = "(3) test" if subset=="test"

save data/predictions/preds_small_mw_clean, replace



****************************************************************************************
****************  Table 1 and Appendix Tables 5 and 6, Baseline Results ****************
****************************************************************************************

foreach s in large small {
	
	use data/predictions/preds_`s'_national_clean, clear
	
	matrix table_baseline_inc_`s' = J(2,6,.)
	matrix table_baseline_pop_`s' = J(2,6,.)

	matrix table_baseline_byyear_inc_`s' = J(2,9,.)
	matrix table_baseline_byyear_pop_`s' = J(2,9,.)

	** Income and Population Levels
	foreach o in inc pop {
		local row = 0
		local col = 1
		foreach f in "_feature" "" {
			local row = `row'+1
			preserve
			
			foreach t in 0 10 {
				quietly sum true_`o'_`t'
				gen tss_`t' = (true_`o'_`t' - r(mean))^2
				gen ssr_`t' = (`o'_`t'_base`f' - true_`o'_`t')^2
			}
			gen one = 1
			collapse (sum) one tss* ssr* if ssr_0!=. & ssr_10!=., by(subset)
			di "`s' img levels sample size = " one[1]+one[2]+one[3]
			gen tss = tss_0 + tss_10
			gen ssr = ssr_0+ssr_10
			gen r2 = 1-(ssr/tss)
			gen r2_0 = 1-(ssr_0/tss_0)
			gen r2_10 = 1-(ssr_10/tss_10)
			
			di "prediction accuracy for `s' img `o' levels 00 and 10 `f'"
			list subset r2
			matrix table_baseline_`o'_`s'[`row',`col']==r2[1]
			matrix table_baseline_`o'_`s'[`row',`col'+1]==r2[2]
			matrix table_baseline_`o'_`s'[`row',`col'+2]==r2[3]
			
			//broken down by years
			matrix table_baseline_byyear_`o'_`s'[`row',`col']==r2_0[1]
			matrix table_baseline_byyear_`o'_`s'[`row',`col'+1]==r2_0[2]
			matrix table_baseline_byyear_`o'_`s'[`row',`col'+2]==r2_0[3]
			matrix table_baseline_byyear_`o'_`s'[`row',`col'+3]==r2_10[1]
			matrix table_baseline_byyear_`o'_`s'[`row',`col'+4]==r2_10[2]
			matrix table_baseline_byyear_`o'_`s'[`row',`col'+5]==r2_10[3]
					
			restore
		}
	}

	** Income and Population Differences
	foreach o in inc pop {
		local row = 0
		local col = 4
		foreach f in "_feature" "" {
			local row = `row'+1
			preserve
			quietly sum true_d`o'_0_10
			gen tss = (true_d`o'_0_10 - r(mean))^2
			gen ssr = (d`o'_010_base`f' - true_d`o'_0_10)^2
			gen one = 1
			collapse (sum) one tss ssr if ssr!=., by(subset)
			di "`s' img diffs sample size = " one[1]+one[2]+one[3]
			gen r2 = 1-(ssr/tss)
			di "prediction accuracy for `s' img `o' difference 00 to 10 `f'"
			list subset r2
			matrix table_baseline_`o'_`s'[`row',`col']==r2[1]
			matrix table_baseline_`o'_`s'[`row',`col'+1]==r2[2]
			matrix table_baseline_`o'_`s'[`row',`col'+2]==r2[3]
			
			matrix table_baseline_byyear_`o'_`s'[`row',`col'+3]==r2[1]
			matrix table_baseline_byyear_`o'_`s'[`row',`col'+4]==r2[2]
			matrix table_baseline_byyear_`o'_`s'[`row',`col'+5]==r2[3]
					
			restore
		}
		matlist table_baseline_`o'_`s'
		matlist table_baseline_byyear_`o'_`s'
		
		matrix rownames table_baseline_`o'_`s' = "With Initial Conditions" "Without Initial Conditions"
		matrix rownames table_baseline_byyear_`o'_`s' = "With Initial Conditions" "Without Initial Conditions"

		esttab matrix(table_baseline_`o'_`s', fmt(%10.4f)) using results/table_baseline_`o'_`s'.tex, booktabs fragment nomtitles posthead("")  collabels(none) replace
		esttab matrix(table_baseline_byyear_`o'_`s', fmt(%10.4f)) using results/table_baseline_byyear_`o'_`s'.tex, booktabs fragment nomtitles posthead("")  collabels(none) replace
	}
}



************************************************************************************************
****************		  TABLE 2: Out-of-period model (2.4km Images)			****************
************************************************************************************************


use data/predictions/preds_large_national_clean, clear

matrix table_oop_pop = J(2,5,.)
matrix table_oop_inc = J(2,5,.)

//in-sample levels and diffs
foreach o in pop inc { 
	local row = 0
	local col = 1
	foreach f in "_feature" "" {
		local row = `row'+1
		//levels
		preserve
		foreach t in 0 10 {
			quietly sum true_`o'_`t'
			gen tss_`t' = (true_`o'_`t' - r(mean))^2
			gen ssr_`t' = (`o'_`t'`f'_oos - true_`o'_`t')^2
		}
		collapse (sum) tss* ssr* if tss_0!=. & ssr_0!=.
		gen tss = tss_0 + tss_10
		gen ssr = ssr_0+ssr_10
		gen r2 = 1-(ssr/tss)
		di "prediction accuracy for large img `o' levels 00 and 10 `f'"
		list r2*
		matrix table_oop_`o'[`row',`col']==r2[1]
		restore
		
		local col = `col'+1 
		
		//diffs
		preserve
		quietly sum true_d`o'_0_10
		gen tss = (true_d`o'_0_10 - r(mean))^2
		gen ssr = (d`o'_0_10`f'_oos - true_d`o'_0_10)^2
		collapse (sum) tss ssr if tss!=. & ssr!=.
		gen r2 = 1-(ssr/tss)
		di "prediction accuracy for large img `o' difference 00 to 10 `f'"
		list r2
		matrix table_oop_`o'[`row',`col']==r2[1]
		restore
		
		local col = `col'-1
	}
}

matlist table_oop_pop
matlist table_oop_inc


local row = 0
local col = 3
//out-period population levels and diffs
foreach f in "_feature" "" {
	local row = `row'+1
	//levels
	preserve
	quietly sum true_pop_20
	gen tss = (true_pop_20 - r(mean))^2
	gen ssr = (pop_19`f'_oos - true_pop_20)^2
	
	collapse (sum) tss ssr if tss!=. & ssr!=.
	gen r2 = 1-(ssr/tss)
	di "prediction accuracy for large img pop levels 20 `f'"
	list r2*
	matrix table_oop_pop[`row',`col']==r2[1]
	restore

	local col = `col'+1 

	//10 to 20
	preserve
	quietly sum true_dpop_10_20
	gen tss = (true_dpop_10_20 - r(mean))^2
	gen ssr = (dpop_9_19`f'_oos - true_dpop_10_20)^2
	collapse (sum) tss ssr if tss!=. & ssr!=.
	gen r2 = 1-(ssr/tss)
	di "prediction accuracy for large img pop difference 10 to 20 `f'"
	list r2
	matrix table_oop_pop[`row',`col']==r2[1]
	restore
	
	local col = `col'+1 
	
	//00 to 20
	preserve
	quietly sum true_dpop_0_20
	gen tss = (true_dpop_0_20 - r(mean))^2
	gen ssr = (dpop_0_19`f'_oos - true_dpop_0_20)^2
	collapse (sum) tss ssr if tss!=. & ssr!=.
	gen r2 = 1-(ssr/tss)
	di "prediction accuracy for large img pop difference 00 to 20 `f'"
	list r2
	matrix table_oop_pop[`row',`col']==r2[1]
	restore
	
	local col = `col'-2 

}

//out-period income levels and diffs
local row = 0
local col = 3
foreach f in "_feature" "" {
	local row = `row'+1

	//levels
	preserve
	foreach t in 7 17 {
		quietly sum true_inc_`t'
		gen tss_`t' = (true_inc_`t' - r(mean))^2
		gen ssr_`t' = (inc_`t'`f'_oos - true_inc_`t')^2
	}
	collapse (sum) tss* ssr* if tss_17!=. & ssr_17!=.

	/* fit is .89 in both 07 and 17
	gen r2_7 = 1-(ssr_7/tss_7)
	di r2_7[1]
	gen r2_17 = 1-(ssr_17/tss_17)
	di r2_17[1]
	*/

	gen r2 = 1-(ssr_17/tss_17)
	di "prediction accuracy for large img inc levels 17 `f'"
	list r2*
	matrix table_oop_inc[`row',`col']==r2[1]
	restore

	local col = `col'+1 

	//7 to 17
	preserve
	quietly sum true_dinc_7_17
	gen tss = (true_dinc_7_17 - r(mean))^2
	gen ssr = (dinc_7_17`f'_oos - true_dinc_7_17)^2
	collapse (sum) tss ssr if tss!=. & ssr!=.
	gen r2 = 1-(ssr/tss)
	di "prediction accuracy for large img inc difference 7 to 17 `f'"
	list r2
	matrix table_oop_inc[`row',`col']==r2[1]
	restore
	
	local col = `col'+1 

	//00 to 17
	preserve
	quietly sum true_dinc_0_17
	gen tss = (true_dinc_0_17 - r(mean))^2
	gen ssr = (dinc_0_17`f'_oos - true_dinc_0_17)^2
	collapse (sum) tss ssr if tss!=. & ssr!=.
	gen r2 = 1-(ssr/tss)
	di "prediction accuracy for large img inc difference 00 to 17 `f'"
	list r2
	matrix table_oop_inc[`row',`col']==r2[1]
	restore
	
	local col = `col'-2 
}

foreach o in inc pop {
	matrix rownames table_oop_`o' = "With Initial Conditions" "Without Initial Conditions"

	esttab matrix(table_oop_`o', fmt(%10.4f)) using results/table_oop_`o'.tex, booktabs fragment nomtitles posthead("")  collabels(none) replace
}







**********************************************************************************
***********		 Appendix Table 1: Prediction Error Correlations    **************
**********************************************************************************

{

use data/predictions/preds_large_national_clean, clear
keep if subset=="(3) test"

keep img_id inc_0_base_feature pop_0_base_feature inc_10_base_feature pop_10_base_feature dinc_010_base_feature dpop_010_base_feature true_pop_0 true_pop_10 true_inc_0 true_inc_10 true_dinc_0_10 true_dpop_0_10 ///
fnum county state true_inc_cnty_0 true_inc_cnty_10 true_pop_cnty_0 true_pop_cnty_10  white_0 black_0 hispanic_0 workage_0 female_0 groupshare_0 emp_sec1_0 emp_sec2_0 emp_sec3_0 emp_sec4_0 emp_sec5_0 emp_sec6_0 emp_sec7_0 emp_sec8_0 emp_sec9_0 emp_sec10_0 emp_sec11_0 emp_sec12_0 emp_sec13_0 emp_sec14_0 emp_sec15_0 emp_sec16_0 emp_sec17_0 emp_sec18_0 emp_sec19_0 emp_sec20_0 emp_bus_serv_0 emp_nonbus_serv_0 emp_prod_0 emp_bus_serv_cnty_0 emp_nonbus_serv_cnty_0 emp_prod_cnty_0

rename *_base_feature *
rename *_0 *1
rename *_10 *2
rename true_d*_02 true_d*

reshape long pop inc true_inc true_pop true_inc_cnty true_pop_cnty, i(img_id) j(year)


gen error_inc = inc-true_inc
gen error_pop = pop-true_pop

gen error_dinc = dinc_010 - true_dinc if year==1
gen error_dpop = dpop_010 - true_dpop if year==1


// pred ereror by blob (contiguous urban area)
matrix geo_fes = J(1,4,.)
reg error_inc i.fnum
matrix geo_fes[1,1]=e(r2)
reg error_dinc i.fnum
matrix geo_fes[1,2]=e(r2)
reg error_pop i.fnum
matrix geo_fes[1,3]=e(r2)
reg error_dpop i.fnum
matrix geo_fes[1,4]=e(r2)

esttab matrix(geo_fes, fmt(%5.4fc %5.4fc %5.4fc %5.4fc)) using results/error_geo_fes.tex, ///
fragment booktabs replace varwidth(45) nomtit msign(--) substitute("c1" "" "c2" "" "c3" "" "c4" "" "\midrule" "")

matlist geo_fes


foreach v of varlist white black hispanic workage female groupshare emp_sec* emp_bus_serv1 emp_nonbus_serv1 emp_prod1 emp_bus_serv_cnty emp_nonbus_serv_cnty emp_prod_cnty {
	replace `v' = . if year==2
}

local i = 0
matrix corrs = J(34,4,.)
foreach v of varlist  true_pop_cnty true_inc_cnty white black hispanic workage female groupshare emp_sec* emp_bus_serv1 emp_nonbus_serv1 emp_prod1 emp_bus_serv_cnty emp_nonbus_serv_cnty emp_prod_cnty { 
	di "`v'"
	local i = `i'+1
	corr error_inc `v'
	matrix corrs[`i',1] = r(rho)
	corr error_dinc `v'
	matrix corrs[`i',2] = r(rho)
	corr error_pop `v' 
	matrix corrs[`i',3] = r(rho)
	corr error_dpop `v'
	matrix corrs[`i',4] = r(rho)
	local lab`i' = "`v'"
}

preserve
clear
svmat corrs
//order : inc level, inc diff, pop level, pop diff
rename corrs1 corr_inc
rename corrs2 corr_dinc
rename corrs3 corr_pop
rename corrs4 corr_dpop

gen varname = ""
forval j = 1/`i' {
	replace varname = "`lab`j''" in `j'
}
order varname 

gen sortvar = 1-abs(corr_inc)
sort sortvar
drop sortvar

mkmat corr_inc corr_dinc corr_pop corr_dpop, matrix(corr_out) rownames(varname)


esttab matrix(corr_out, fmt(%5.4fc %5.4fc %5.4fc %5.4fc)) using results/error_corrs.tex,  ///
fragment booktabs replace varwidth(45) nomtit msign(--)

sum corr_dinc, d


restore


}

************************************************************************************************
****************		APPENDIX TABLE 2, Income Per Capita			****************
************************************************************************************************

foreach s in large small {
	
	use data/predictions/preds_`s'_national_clean, clear

	matrix table_baseline_inc_pop_`s' = J(2,6,.)

	** Income per capita Levels
	local row = 0
	local col = 1
	foreach f in "_feature" "" {
		local row = `row'+1
		preserve
		
		foreach t in 0 10 {
			quietly sum true_inc_pop_`t'
			gen tss_`t' = (true_inc_pop_`t' - r(mean))^2
			gen ssr_`t' = (inc_pop_`t'_base`f' - true_inc_pop_`t')^2
		}
		gen one = 1
		collapse (sum) one tss* ssr* if ssr_0!=. & ssr_10!=., by(subset)
		di "`s' img levels sample size = " one[1]+one[2]+one[3]
		gen tss = tss_0 + tss_10
		gen ssr = ssr_0+ssr_10
		gen r2 = 1-(ssr/tss)
		di "prediction accuracy for `s' img inc_pop levels 00 and 10 `f'"
		list subset r2
		matrix table_baseline_inc_pop_`s'[`row',`col']==r2[1]
		matrix table_baseline_inc_pop_`s'[`row',`col'+1]==r2[2]
		matrix table_baseline_inc_pop_`s'[`row',`col'+2]==r2[3]
		restore
	}


	** Income and Population Differences
	local row = 0
	local col = 4
	foreach f in "_feature" "" {
		local row = `row'+1
		preserve
		quietly sum true_dinc_pop_0_10
		gen tss = (true_dinc_pop_0_10 - r(mean))^2
		gen ssr = (dinc_pop_010_base`f' - true_dinc_pop_0_10)^2
		gen one = 1
		collapse (sum) one tss ssr if ssr!=., by(subset)
		di "`s' img diffs sample size = " one[1]+one[2]+one[3]
		gen r2 = 1-(ssr/tss)
		di "prediction accuracy for `s' img inc_pop difference 00 to 10 `f'"
		list subset r2
		matrix table_baseline_inc_pop_`s'[`row',`col']==r2[1]
		matrix table_baseline_inc_pop_`s'[`row',`col'+1]==r2[2]
		matrix table_baseline_inc_pop_`s'[`row',`col'+2]==r2[3]
		restore
	}
	matlist table_baseline_inc_pop_`s'
	matrix rownames table_baseline_inc_pop_`s' = "With Initial Conditions" "Without Initial Conditions"

	esttab matrix(table_baseline_inc_pop_`s', fmt(%10.4f)) using results/table_baseline_inc_pop_`s'.tex, booktabs fragment nomtitles posthead("")  collabels(none) replace
}



************************************************************************************************
****************		APPENDIX TABLE 3, Breakdown by Bands (2.4km Images)		****************
************************************************************************************************

use data/predictions/preds_large_national_clean, clear

matrix table_bands_inc_large = J(2,6,.)
matrix table_bands_pop_large = J(2,6,.)

** Income and Population Levels
foreach o in inc pop {
	local row = 0
	
	foreach f in "_feature" "" {
		local col = 0
		local row = `row'+1
		
		foreach s in RGB base nl {
			local col = `col'+1
			preserve			
			foreach t in 0 10 {
				quietly sum true_`o'_`t'
				gen tss_`t' = (true_`o'_`t' - r(mean))^2
				gen ssr_`t' = (`o'_`t'_`s'`f' - true_`o'_`t')^2
			}
			collapse (sum) tss* ssr* if ssr_0!=. & ssr_10!=., by(subset)
			gen tss = tss_0 + tss_10
			gen ssr = ssr_0+ssr_10
			gen r2 = 1-(ssr/tss)
			di "prediction accuracy for large img `o' levels 00 and 10 using `s' `f'"
			list subset r2
			matrix table_bands_`o'_large[`row',`col']==r2[3]
			restore
		}
	}
}
//matlist table_bands_pop_large


** Income and Population Differences
foreach o in inc pop {
	local row = 0

	foreach f in "_feature" "" {
		local col = 3
		local row = `row'+1
	
		foreach s in RGB base nl {
			local col = `col'+1
			preserve
			quietly sum true_d`o'_0_10
			gen tss = (true_d`o'_0_10 - r(mean))^2
			gen ssr = (d`o'_010_`s'`f' - true_d`o'_0_10)^2
			collapse (sum) tss ssr if ssr!=., by(subset)
			gen r2 = 1-(ssr/tss)
			di "prediction accuracy for large img `o' difference 00 to 10 using `s' `f'"
			list subset r2
			matrix table_bands_`o'_large[`row',`col']==r2[3]
			restore
		}
	}
	
	matrix rownames table_bands_`o'_large = "With Initial Conditions" "Without Initial Conditions"

	esttab matrix(table_bands_`o'_large, fmt(%10.4f)) using results/table_bands_`o'.tex, booktabs fragment nomtitles posthead("")  collabels(none) replace
	
}





************************************************************************************************
****************		APPENDIX TABLE 4 Impact of Resolution (1.2km Images)		************
************************************************************************************************
*note: high is 15m resolution, otherwise 30m resolution


use data/predictions/preds_small_mw_clean, clear

matrix table_res_inc = J(2,4,.)
matrix table_res_pop = J(2,4,.)

** Income and Population Levels
foreach o in inc pop {
	local row = 0
	
	foreach f in "_feature" "" {
		local col = 0
		local row = `row'+1

		foreach r in "" "_high" {
			local col = `col'+1
			preserve
			
			foreach t in 0 10 {
				quietly sum true_`o'_`t'
				gen tss_`t' = (true_`o'_`t' - r(mean))^2
				gen ssr_`t' = (`o'_`t'_RGB`f'`r' - true_`o'_`t')^2
			}
			collapse (sum) tss* ssr* if ssr_10!=. & ssr_0!=., by(subset)
			gen tss = tss_0 + tss_10
			gen ssr = ssr_0+ssr_10
			gen r2 = 1-(ssr/tss)
			di "prediction accuracy for mid-atlantic small img `o' levels 00 and 10 `f' `r'"
			list subset r2
			matrix table_res_`o'[`row',`col']==r2[3]

			restore
		}
	}
}

** Income and Population Differences
foreach o in inc pop {
	local row = 0

	foreach f in "_feature" "" {
		local col = 2
		local row = `row'+1
		
		foreach r in "" "_high" {
			local col = `col'+1
			
			preserve
			quietly sum true_d`o'_0_10
			gen tss = (true_d`o'_0_10 - r(mean))^2
			gen ssr = (d`o'_010_RGB`f'`r' - true_d`o'_0_10)^2
			collapse (sum) tss ssr if ssr!=., by(subset)
			gen r2 = 1-(ssr/tss)
			di "prediction accuracy for mid-atlantic small img `o' difference 00 to 10 `f' `r'"
			list subset r2
			matrix table_res_`o'[`row',`col']==r2[3]

			restore
		}
	}
	
	matlist table_res_`o'
	matrix rownames table_res_`o' = "With Initial Conditions" "Without Initial Conditions"

	esttab matrix(table_res_`o', fmt(%10.4f)) using results/table_res_`o'.tex, booktabs fragment nomtitles posthead("")  collabels(none) replace

}





////// Sources of reported statistics on counties, block  groups, and blocks in manuscript
/*
Continental land area for US: 8,080,464.3 km2  (https://en.wikipedia.org/wiki/Contiguous_United_States)

Number of counties in continental US in 2000: 3002 (excluding AK and HI and counting independent cities in the US as part of their surrounding counties) (https://www2.census.gov/geo/pdfs/reference/GARM/Ch4GARM.pdf)
(8080464.3/3002)^.5 = 51.9

Census Block Groups have 600 to 3000 people https://www.census.gov/programs-surveys/geography/about/glossary.html#par_textimage_4.  

In 2000 there were 8,262,363 Census Blocks and 211,267  Block Groups for a mean of 39 Blocks per Group (https://www2.census.gov/geo/pdfs/maps-data/data/changes_census_blocks_2000_2010.pdf)
*/




