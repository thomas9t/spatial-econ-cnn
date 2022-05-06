
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


**********************************************************
***********		  Cleaning Data		 		**************
**********************************************************

//this section cleans exports of cencus block-level and image-level nightlight intensity measures extracted from google earth engine
//the output of this commented section is made available in our data repo, the underlying raw exports (i.e. dmps00rawsum_blocks_080of5.csv) are approximately 30gb in total and can be recreated using the Google Engine python code code\extract_imagery\export_nightlights_[blocks/images].py in this repository
{
/*
quietly {
foreach y in "00" "10" {
	foreach f in "01" "04" "05" "06" "08" "09" "10" "11" "12" "13" "19" "16" "17" "18" "20" "21" "22" "25" "24" "23" "26" "27" "29" "28" "30" "37" "38" "31" "33" "34" "35" "32" "36" "39" "40" "41" "42" "44" "45" "46" "47" "48" "49" "51" "50" "53" "55" "54" "56" {
	//for testing: foreach f in "01" "06" {		
		noisily di "Starting 20`y' `f'"
		clear
		capture import delimited "data/nightlights/dmps`y'rawsum_blocks_`f'0of5.csv", clear
		if _N==0 capture import delimited "data/nightlights/dmps`y'rawsum_blocks_`f'0.csv", clear
		if _N==0 {
			foreach p in "-1" "1" "2" "3" "4" "5" {
				import delimited "data/nightlights/dmps`y'rawsum_blocks_`f'`p'of5.csv", clear
				capture append using `blocks_`y'_`f''
				if "`p'"=="-1" tempfile blocks_`y'_`f'
				if "`p'"!="5" save `blocks_`y'_`f'', replace
			}
		}
		drop geo partflg housing10 systemindex blockid10 pop10
		tostring statefp10 countyfp10 tractce10 blockce, replace
		gen ls = length(statefp10)
		gen lc = length(countyfp10)
		gen lt = length(tractce10)
		gen lb = length(blockce)
		gen gisjoin = "G"+((2-ls)*"0")+statefp10+"0"+((3-lc)*"0")+countyfp10+"0"+((6-lt)*"0")+tractce10+((4-lb)*"0")+blockce
		keep gisjoin sum
		rename sum dmsp_`y'
		if "`f'"=="01" tempfile block_dmsp`y'
		else append using `block_dmsp`y''
		save `block_dmsp`y'', replace
	}
}
}
		
use `block_dmsp00',clear
merge 1:1 gisjoin using `block_dmsp10', nogen
save data/nightlights/block_rawdmsp_merged_00_10, replace
*/

/*
//these are GEE exports of image level nightlights
foreach s in "large" "small" {
	foreach y in "00" "10" {
		import delimited using data/nightlights/dmsprawsum_`s'imgs_`y'.csv, clear
		rename sum dmsp_`y'
		keep img_id dmsp_`y'
		if "`y'"=="00" {
			tempfile dmsp00
			save `dmsp00', replace
		}
		if "`y'"=="10" {
			merge 1:1 img_id using `dmsp00', assert(3) nogen			
			
			//merge in block based image labels
			merge 1:1 img_id using "data\labels\blockcw_labelled_imgs_national_`s'", nogen keep(3) assert(2 3)
			
			keep img_id dmsp_00 dmsp_10 log_pop_00 log_pop_10 log_inc_00 log_inc_10 popshare_00


			//weights
			gen praw = log_pop_00
			rename popshare_00 pshare
			rename *_00 *1
			rename *_10 *2
			reshape long dmsp log_pop log_inc, i(img_id) j(y)
			recode y (1=2000) (2=2010), gen(year)
			drop y
			
			keep if pshare<.85
			rename log_* *
			foreach v of varlist dmsp inc pop {
				sort img_id year
				gen d_`v' = `v'-`v'[_n-1] if year==2010 & img_id==img_id[_n-1]
			}
			
			save data/nightlights/`s'img_dmsplabelled_merged_00_10, replace
		}
	}
}
*/


//This section cleans the above intermediate files and merges in additional fields from phase 1 for geographic comparisons. 
//The segment is commented out because the output of it (block_rawdmsp_labelled_00_10) is included as an intermediate file in the repository, so only those interested in replicating the creation of this intermediate file would want to run this segment.
/*	   
use data/nightlights/block_rawdmsp_merged_00_10, clear
merge 1:1 gisjoin using data/labels/generated_files/block_labels_cw, keep(3) nogen

foreach v in `initials' {
	rename `v'_00 `v'
}
keep gisjoin dmsp_00 dmsp_10 pop_00 pop_10 inc_00 inc_10 popshare_00


//state/county/czone codes
gen gid = substr(gisjoin,1,15)


preserve
//USDA Economic Research Service at https://www.ers.usda.gov/data-products/commuting-zones-and-labor-market-areas/
import excel using data/labels/nightlights/county_to_cz.xls, clear firstrow
drop CountyName
rename FIPS county
rename CommutingZoneID1990 czone
destring *, replace
sort county
tempfile cz
save `cz'
restore

preserve
import delimited using data/labels/source_files/nhgis0065_ds191_20125_2012_blck_grp.csv, clear
keep if qw4e001!=.
keep gisjoin
rename gisjoin gid
gen state = substr(gid,2,2)
gen county = substr(gid,2,2) + substr(gid,5,3)
destring county, replace
merge m:1 county using `cz'
tempfile codes
save `codes'
restore


merge m:1 gid using `codes', keep(3) nogen
rename gid bg
*bg county czone state 

merge 1:1 gisjoin using data/labels/block_areas10, keep(3) nogen


//for weights
gen praw = pop_00

rename popshare_00 pshare
rename *_00 *1
rename *_10 *2
reshape long dmsp pop inc, i(gisjoin) j(y)
recode y (1=2000) (2=2010), gen(year)
drop y

save data/nightlights/block_rawdmsp_labelled_00_10, replace

}

*/


**********************************************************
***********		   Geography range graph	**************
**********************************************************

{
*
use data/nightlights/block_rawdmsp_labelled_00_10, clear
keep if year==2010
//shape area is in square meters, converting to square kilometers
replace shape_area = shape_area*.000001

//excluding DC here
drop if state=="11"

//local low "p25"
local low "p10"
//local low "min"
//local high "p75"
local high "p90"
//local high "max"

sum shape_area, d
matrix areas = r(`low'), r(p50), r(`high')

local bglist "(firstnm) county czone state"
local countylist "(firstnm) czone state"
local czonelist "(firstnm) state"
local statelist ""

foreach g in bg county czone state {
	collapse (sum) shape_area ``g'list', by(`g')
	sum shape_area, d
	matrix areas = areas \ r(`low'), r(p50), r(`high')
	
	if "`g'"=="bg" {
		matrix areas = areas \ 1.44, 1.44, 1.44 
		matrix areas = areas \ 5.76, 5.76, 5.76
	}
}



matlist areas
clear
svmat areas
gen geo = 8-_n
label define geos 1 "Block" 2 "Small Img" 3 "Large Img" 4 "Block Group" 5 "County" 6 "Commuting Zone" 7 "State"
label values geo geos
rename areas1 low
rename areas2 med
rename areas3 high 
foreach v in low med high {
	replace `v' = log(`v')
}

gen med_label = exp(med)

twoway (rspike low high geo, color(gs10) lw(slim)) (scatter med geo, mlabel(med_label) mlabp(3) mlabc(black) mlabf(%20.2fc) mlabs(small) mcolor(black) msa(90) msym(pipe)) ///
, legend(off) plotregion(lw(none)) ylabel(-4.6051702 "0.01" 0 "1" 4.605 "100" 9.2103404 "10K" 13.815511 "1M", angle(horizontal)) ///
ytitle("Geography Area ( km{sup:2})") ///
xlabel(1 "State" 2 "Commuting Zone" 3 "County" 4 "2.4km Image" 5 "1.2km Image" 6 "Block Group" 7 "Block", labs(small)) xtitle("") xscale(range(.9 7.1))

//graph export "results/shape_size.eps", font("Times New Roman") replace
graph export "results/figure1.eps", font("Times New Roman") replace

}



******************************************************************
***********		  R2 of Night Lights by Geography	**************
******************************************************************

{
*

matrix r2 = J(7,4,.)

local wt "[aw = praw]"

local i = 2
foreach s in "small" "large" {

	local i = `i'+1

	use data/nightlights/`s'img_dmsplabelled_merged_00_10, clear

	//levels
	reg inc dmsp `wt', robust 
	matrix r2[`i',1]=e(r2)
	reg pop dmsp `wt', robust 
	matrix r2[`i',2]=e(r2)
	//diffs
	reg d_inc d_dmsp `wt', robust 
	matrix r2[`i',3]=e(r2)
	reg d_pop d_dmsp `wt', robust 
	matrix r2[`i',4]=e(r2)

}
matlist r2

*
use data/nightlights/block_rawdmsp_labelled_00_10, clear

local gisjoinup "county"
local bgup "czone"
local countyup "state"
local czoneup "state"
local stateup "state"

local i = 0 
foreach g in gisjoin bg county czone state {
	local i = `i'+1
	if "`g'"=="county" local i = `i'+2
	preserve
	
	if "`g'"!="gisjoin" {
		collapse (sum) pop inc dmsp praw shape_area , by(`g' year)
		gen pd = pop / shape_area
		gen negpopd = -pd
		gen negpop = -pop
		sort negpopd negpop
		gen sumpop = sum(pop) 
		sort negpopd negpop
		egen tpop = total(pop)
		sort negpopd negpop
		gen pshare = sumpop/tpop
		drop pd negpopd negpop sumpop tpop
	}
	
	if "`g'"!="state" keep if pshare<.85
	
	foreach v of varlist dmsp inc pop {
		replace `v' = log(`v'/shape_area)
		sort `g' year
		gen d_`v' = `v'-`v'[_n-1] if year==2010 & `g'==`g'[_n-1]
	}
	

	di "Reg results by `g'"
	
	//levels
	reg inc dmsp `wt', robust 
	matrix r2[`i',1]=e(r2)
	
	reg pop dmsp `wt', robust 
	matrix r2[`i',2]=e(r2)

	//diffs
	reg d_inc d_dmsp `wt', robust 
	matrix r2[`i',3]=e(r2)
	
	reg d_pop d_dmsp `wt', robust 
	matrix r2[`i',4]=e(r2)
	restore
}

matlist r2

clear
svmat r2
gen geo = 8-_n

twoway (line r21 geo, lcolor(navy) lw(thick)) (scatter r21 geo, color(navy)) (line r22 geo, lcolor(sienna) lw(thick)) (scatter r22 geo, color(sienna))  ///
(line r23 geo, lcolor(blue) lw(thick)) (scatter r23 geo, color(blue))  (line r24 geo, lcolor(orange) lw(thick)) (scatter r24 geo, color(orange)) ///
, xlabel(1 "State" 2 "Commuting Zone" 3 "County" 4 "2.4km Image" 5 "1.2km Image" 6 "Block Group" 7 "Block", labs(small)) ///
legend(label(1 "Income Level") label(3 "Population Level") label(5 "Income Difference") label(7 "Population Difference") ring(0) position(2) col(1) order(1 3 5 7)) ///
ylabel(0(.25)1, angle(horizontal)) plotregion(lw(none)) yscale(range(0 1)) ytitle("R{superscript:2}") xtitle("")

//graph export results/dmsp_r2_levdiff_wimgs_00_10.eps, font("Times New Roman") replace
graph export "results/figure3.eps", font("Times New Roman") replace

}




******************************************************************
***********		  Scatter Plots of CNN model fit	**************
******************************************************************

{
*
//this data is generated in "replicate draft r2 stats.do"
use data/predictions/preds_large_national_clean, clear
keep if subset=="(3) test"

keep img_id inc_0_base_feature inc_10_base_feature dinc_010_base_feature true_inc_0 true_inc_10 true_dinc_0_10 pop_0_base_feature pop_10_base_feature dpop_010_base_feature true_pop_0 true_pop_10 true_dpop_0_10

rename *inc_0* *inc1
rename *inc_10* *inc2
rename *pop_0* *pop1
rename *pop_10* *pop2
rename d*1 d*
rename true_d*1 true_d*

reshape long true_inc true_pop inc pop, i(img_id) j(y)

recode y (1=2000) (2=2010), gen(year)
drop y
order img_id year

foreach v of varlist *d* {
	replace `v' = . if year==2000
}


//		Income 

twoway (scatter inc true_inc, ms(Oh) msize(tiny) mcolor(dkorange%20) ) (line true_inc true_inc if true_inc>13 & true_inc<21, lcolor(black) lwidth(thin)) if true_inc>6, ///
xlabel(8(4)22) ylabel(13(2)21, angle(horizontal)) ytitle("Predicted Log Income") xtitle("Log Income") legend(off)  ///
plotregion(lcolor(none)) text(21.5 21.3 "45 deg", size(vsmall)) title("Income Level: R{sup:2}=0.90", size(medium)) name(ilev)


twoway (scatter dinc true_dinc if dinc<50,  ms(Oh) msize(tiny) mcolor(dkorange%20)) (line true_dinc true_dinc if true_dinc>0 & true_dinc<2.5, lcolor(black) lwidth(thin)) if true_dinc>-2 & true_dinc<3 & dinc<4, ///
xlabel(-2(1)3) ylabel(0(1)4, angle(horizontal)) ytitle("Predicted Log Income Change") xtitle("Log Income Change") legend(off) ///
plotregion(lcolor(none)) text(2.7 2.7 "45 deg", size(vsmall)) title("Income Difference: R{sup:2}=0.40", size(medium)) name(idiff)

//		Population

twoway (scatter pop true_pop, ms(Oh) msize(tiny) mcolor(dkorange%20)) (line true_pop true_pop if true_pop>-1, lcolor(black) lwidth(thin)) if pop>-1.5 & true_pop>-1.5, ///
xlabel(-1(3)11) ylabel(0(4)12, angle(horizontal)) ytitle("Predicted Log Population") xtitle("Log Population") legend(off) ///
plotregion(lcolor(none)) text(12.3 11.5 "45 deg", size(vsmall)) title("Population Level: R{sup:2}=0.91", size(medium)) name(plev)

twoway (scatter dpop true_dpop, msize(tiny) mcolor(dkorange%20) mlwidth(none)) (line true_dpop true_dpop if true_dpop>-1 & true_dpop<3, lcolor(black) lwidth(thin)) if true_dpop>-2 & true_dpop<4 & dpop<4, ///
xlabel(-2(2)4) ylabel(-1(1)4, angle(horizontal))  ytitle("Predicted Log Population Change") xtitle("Log Population Change") legend(off) ///
plotregion(lcolor(none)) text(3.3 3.3 "45 deg", size(vsmall)) title("Population Difference: R{sup:2}=0.46", size(medium)) name(pdiff)

graph combine ilev plev idiff pdiff

//graph export results/inc_pop_fits.png, replace width(2000)
graph export "results/figure2.eps", font("Times New Roman") replace

}






**************************************************************************************
***********		 Approximate Share of Population in Large Image Sample	**************
**************************************************************************************

use data/predictions/preds_large_national_clean, clear

replace true_pop_0= exp(true_pop_0)
collapse (sum) true_pop_0
di true_pop_0[1]/281421906
//approximately 93% of US population
//2000 total population estimate is from https://www.census.gov/prod/cen2010/briefs/c2010br-01.pdf

