


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


**** Inflation Values for adjusting income

//from https://fred.stlouisfed.org/series/CPIAUCSL
import delimited using data\labels\source_files\CPIAUCSL.csv, clear
rename cpiaucsl infl
gen d = date(date,"YMD",2019)
format d %td
gen year = year(d)

collapse (mean) infl, by(year)

sum infl if y==2012

replace infl = r(mean)/infl

sum infl if y==1999
*inflating 1999 dollars by 1.3782055 to get 2012 dollars


sum infl if y==2009
*ACS 07:  1.070009
sum infl if y==2017
*ACS 15: .9365731
sum infl if y==2018
*ACS 16: .9143061
sum infl if y==2019
*ACS 17: .8980457




**************    Cleaning Label Data, 2000

*bg group quarters indicator
{
*
import delimited using data\labels\source_files\nhgis0064_ds147_2000_block.csv, clear
rename fxs001 totpop
egen test = rowtotal(f0n*)
replace test = test-totpop
sum test, d
assert r(mean)==0 & r(sd)==0
rename f0n002 grppop

gen groupshare = grppop/totpop
**Groupshare is just for filtering purposes, to exclude images with large shares of people living in groups
** Don't need/want to outright exclude any areas with 0 population for purpose of averaging over image
replace groupshare = 0 if totpop==0

keep gisjoin groupshare
save data\labels\generated_files\groupshare_block, replace
*
}


*block demographics, 2000
{
*
import delimited using data\labels\source_files\nhgis0057_ds147_2000_block.csv, clear
rename fxs001 pop
gen white = fyf001 
gen black = fyf002
egen hispanic = rowtotal(fyf008-fyf014), missing
egen totrac = rowtotal(fyf*), missing
foreach v in white black hispanic {
	replace `v' = `v'/totrac
}

*working age
egen workage= rowtotal(fym009-fym014 fym032-fym037), missing
egen totsex = rowtotal(fym*), missing
replace workage = workage/totsex

*female
egen female = rowtotal(fym024-fym046), missing
replace female = female/totsex


gen gisjoin_bg = substr(gisjoin,1,15)
*implies that there can be at most 10 block groups in each tract!

keep gisjoin* pop white black hispanic workage female

save data\labels\generated_files\demos_block_00, replace


import delimited using data\labels\source_files\nhgis0065_ds152_2000_blck_grp.csv, clear

rename hg5001 inc_bg
keep gisjoin inc_bg
rename gisjoin gisjoin_bg
merge 1:m gisjoin_bg using data\labels\generated_files\demos_block_00, nogen


*generating block income
bysort gisjoin_bg: egen pop_bg = total(pop)
drop if pop_bg==0
gen pshare = pop/pop_bg
gen inc = inc_bg*pshare

*Inflation Adjustment, converting all to 2012 dollars (1999 here), based on calculations above
replace inc = inc*1.3782055

*group pop
merge 1:1 gisjoin using data\labels\generated_files\groupshare_block
drop if _merge!=3
drop _merge
*Exclude block groups with more than 5% of the population living in group quarters (about 10% of high pop block groups)
*drop if groupshare>0.05

gen state = substr(gisjoin,2,2)
destring state, replace
 
drop *_bg

gen county = substr(gisjoin,1,8)
order gisjoin county state
save data\labels\generated_files\demos_inc_block_00, replace
*
}


*county demographics and merging, 2000
{
*
import delimited using data\labels\source_files\nhgis0065_ds147_2000_blck_grp.csv, clear

drop county
gen county = substr(gisjoin,1,8)

collapse (sum) fxs001 fyf* fym* , by(county)


rename fxs001 pop
gen white = fyf001 
gen black = fyf002
egen hispanic = rowtotal(fyf008-fyf014), missing
egen totrac = rowtotal(fyf*), missing
foreach v in white black hispanic {
	replace `v' = `v'/totrac
}

*working age
egen workage= rowtotal(fym009-fym014 fym032-fym037), missing
egen totsex = rowtotal(fym*), missing
replace workage = workage/totsex

*female
egen female = rowtotal(fym024-fym046), missing
replace female = female/totsex

drop fyf* fym* totrac totsex

tempfile demos_county00
save `demos_county00'


import delimited using data\labels\source_files\nhgis0065_ds152_2000_blck_grp.csv, clear
drop county
gen county = substr(gisjoin,1,8)

rename hg5001 inc
collapse (sum) inc, by(county)
replace inc = inc*1.3782055

merge 1:1 county using `demos_county00', nogen
rename * *_cnty
rename county_cnty county

merge 1:m county using demos_inc_block_00, nogen
drop pshare

order gisjoin county state
save data\labels\generated_files\block_labels_00, replace
*
}


** cleaning lodes resident area employment
*note: employment data will merge with 2010 labels, not 2000 ones, because relevant geography is 2010 blocks
{

**create: data\labels\generated_files\lodes_rac_national_2004
local states "al ar az ca co ct dc de fl ga ia id il in ks ky la ma md me mi mn mo ms mt nc nd ne nh nj nm nv ny oh ok or pa ri sc sd tn tx ut va vt wa wi wv wy"
foreach s in `states' {
	capture copy https://lehd.ces.census.gov/data/lodes/LODES7/`s'/rac/`s'_rac_S000_JT00_2004.csv.gz data\labels\source_files\lodes\rac_`s'_2004.gz, replace
}
*unzipped all these gz files using 7zip, just select all zip files -> right click, and hit "Extract Here"
foreach s in `states' {
	import delimited using data\labels\source_files\lodes\`s'_rac_S000_JT00_2004.csv, clear
	rename h_geocode w_geocode
	format w_geocode %30.29f	
	tostring w_geocode , generate(gisjoin) format(%30.29f)
	gen len = length(gisjoin)
	replace gisjoin = "G"+gisjoin if len==15
	replace gisjoin = "G0"+gisjoin if len==14
	replace gisjoin = substr(gisjoin,1,3) + "0" + substr(gisjoin,4,3) + "0" + substr(gisjoin,7,20)
	rename cns* emp_sec*
	rename *sec0* *sec*

	keep gisjoin emp_sec*
	
	if "`s'"!="al" append using data\labels\generated_files\lodes_rac_national_2004
	else tempfile data\labels\generated_files\lodes_rac_national_2004
	save data\labels\generated_files\lodes_rac_national_2004, replace
}


use data\labels\generated_files\lodes_rac_national_2004, clear
rename gisjoin_1 gisjoin
gen county = substr(gisjoin,1,8)

*utilities, trade, transportation, information, finance, prof/bus
egen emp_bus_serv = rowtotal(emp_sec3 emp_sec6 emp_sec7 emp_sec8 emp_sec9 emp_sec10 emp_sec11 emp_sec12 emp_sec13 emp_sec14)
*ed/health, leisure, other, govt
egen emp_nonbus_serv = rowtotal(emp_sec15 emp_sec16 emp_sec17 emp_sec18 emp_sec19 emp_sec20)
*nat res, const, manuf
egen emp_prod = rowtotal(emp_sec1 emp_sec2 emp_sec4 emp_sec5)

sort county
foreach v in bus_serv nonbus_serv prod {
	by county: egen emp_`v'_cnty = total(emp_`v')
}

egen blockemp = rowtotal(emp_sec*)
foreach v of varlist emp_sec* emp_bus_serv emp_nonbus_serv emp_prod {
	replace `v' = `v'/blockemp
}

egen cntyemp = rowtotal(emp_*_cnty)
foreach v of varlist emp_*_cnty {
	replace `v' = `v'/cntyemp
}

drop county
save data\labels\generated_files\lodes_04_2010blocks, replace
*
}



** cleaning ACS 2015, 2016 labels
{
*
import delimited using data\labels\source_files\nhgis0067_ds233_20175_2017_blck_grp.csv, clear
rename ahy1e001 pop_bg15
rename ah21e001 inc_bg15
keep gisjoin *_bg15
*Inflation Adjustment, converting all to 2012 dollars (2017 here), based on infl.do
replace inc_bg15 = inc_bg15*.9365731

rename gisjoin gisjoin_bg
save data\labels\generated_files\acs_15_labels, replace
*
}


** cleaning ACS 2015-2019 labels
{
*
import delimited using data\labels\source_files\nhgis0070_ds244_20195_2019_blck_grp.csv, clear
 
rename alube001 pop_bg17
rename alyfe001 inc_bg17
keep gisjoin *_bg17
*Inflation Adjustment, converting all to 2012 dollars (2018 here), based on infl.do
replace inc_bg17 = inc_bg17*.8980457

rename gisjoin gisjoin_bg
save data\labels\generated_files\acs_17_labels, replace
*
}

** cleaning ACS 2005-2009 labels and crosswalking to 2010 block groups, to merge with 10/15 labels
{
*
import delimited using data\labels\source_files\nhgis0071_ds195_20095_2009_blck_grp.csv, clear

rename rk9e001 pop_bg7
rename rpke001 inc_bg7
keep gisjoin *_bg7
*Inflation Adjustment, converting all to 2012 dollars (2018 here), based on infl.do
replace inc_bg7 = inc_bg7* 1.070009
rename gisjoin gisjoin_bg
tempfile labels7
save `labels7'

//generating bg to block disaggregation weights based on 2000 pop
use data\labels\generated_files\demos_inc_block_00, clear
gen gisjoin_bg  = substr(gisjoin,1,15)
bysort gisjoin_bg: egen pop_bg = total(pop)
gen bg_share = pop/pop_bg
drop pop*

merge m:1 gisjoin_bg using `labels7', keep(3) nogen
replace pop_bg7 = pop_bg7*bg_share
replace inc_bg7 = inc_bg7*bg_share
keep gisjoin pop_bg7 inc_bg7
save `labels7', replace

//This file downloaded from https://www.nhgis.org/geographic-crosswalks and saved as a stata dta file
use data\labels\source_files\nhgis_blk2000_blk2010_gj, clear

merge m:1 gisjoin using `labels7', keep(3) nogen
replace pop_bg7 = pop_bg7*weight
replace inc_bg7 = inc_bg7*weight

gen gisjoin_bg = substr(gjoin2010,1,15)
collapse (sum) *_bg7, by(gisjoin_bg)

sum pop_bg7, d
sum inc_bg7, d

save data\labels\generated_files\acs_7_labels, replace

*
}


{
*clean 2020 population data and crosswalk to 2020
import delimited using data\labels\source_files\nhgis0072_ds248_2020_block.csv, clear
rename U7B001 pop_20
keep gisjoin pop_20

tempfile pop20
save `pop20'


//crosswalk to 2010 blocks
//This file downloaded from https://www.nhgis.org/geographic-crosswalks
import delimited using data\labels\source_files\nhgis_blk2020_blk2010_gj.csv, clear
//non-merged are just PR blocks in cw file
merge m:1 gisjoin using `pop20', nogen keep(3)

//collapsing from full crosswalk to 2010 blocks
replace pop_20 = pop_20*weight
collapse (sum) pop_20, by(gisjoin)

keep gisjoin pop_20

save data\labels\generated_files\block_pop_20, replace
*
}


// Cleaning csv output of block areas
//this section is commented out because the intermediate raw csv files of Census Block areas are not included in this repository, to conserve space. To replicate this stage you would need to export csv versions of NHGIS 2010 block shapefiles to recreate the block10[state].csv files used in the loop below
/*
local states DC AL AZ AR CA CO CT DE FL GA ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY
foreach s in `states' {
	//these are direct csv exports of Census block shapefiles for each state from NHGIS, they contain a block geographic and the geographic area of each block
	import delimited using data\labels\source_files\blocks10`s'.csv, clear
	keep gisjoin shape_area
	capture append using `areas10'
	tempfile areas10
	save `areas10'		
}
save data\labels\generated_files\block_areas10, replace
*/



{
*
** clean labels for 2010 outcomes (income and population), merge with lodes data, then merge all with 2010 block tabulate intersections

*need 2010 block pop, bg income imputed to blocks
import delimited using data\labels\source_files\nhgis0065_ds191_20125_2012_blck_grp.csv, clear
rename qw4e001 inc_bg
keep gisjoin inc_bg
rename gisjoin gisjoin_bg

*
import delimited using data\labels\source_files\nhgis0055_ds172_2010_block.csv, clear
rename h7v001 pop
keep gisjoin pop
gen gisjoin_bg = substr(gisjoin,1,15)
save data\labels\generated_files\block_pop_2010, replace
*


merge 1:1 gisjoin_bg using data\labels\generated_files\acs_15_labels
keep if _merge!=2
drop _merge

merge 1:1 gisjoin_bg using data\labels\generated_files\acs_17_labels, nogen keep(1 3)

merge 1:1 gisjoin_bg using data\labels\generated_files\acs_7_labels, nogen keep(1 3)

merge 1:m gisjoin_bg using data\labels\generated_files\block_pop_2010, nogen keep(3)

merge 1:1 gisjoin using data\labels\generated_files\block_pop_20, nogen keep(match)


*generating block income in 10, 15, 7, 17
bysort gisjoin_bg: egen pop_bg = total(pop)
drop if pop_bg==0
//pop weight in 2010
gen pshare = pop/pop_bg
gen inc = inc_bg*pshare
gen inc_15 = inc_bg15*pshare

gen inc_7 = inc_bg7 *pshare

//distributing 2017 bg income based on block pop weights from 2020
bysort gisjoin_bg: egen pop_bg20 = total(pop_20)
gen pshare20 = pop_20/pop_bg20
gen inc_17 = inc_bg17 * pshare20

keep gisjoin pop inc inc_15 pop_bg inc_bg inc_bg15 pop_bg15 pop_bg7 inc_bg7 pop_bg17 inc_bg17 inc_7 inc_17 pop_20 pop_bg20

rename pop_bg17 pop_bg_17
rename inc_bg17 inc_bg_17
rename pop_bg15 pop_bg_15
rename inc_bg15 inc_bg_15
rename pop_bg7 pop_bg_7
rename inc_bg7 inc_bg_7
rename inc inc_10
rename inc_bg inc_bg_10
rename pop pop_10
rename pop_bg pop_bg_10
rename pop_bg20 pop_bg_20

merge 1:1 gisjoin using data\labels\generated_files\lodes_04_2010blocks
drop if _merge==2
drop _merge

save data\labels\generated_files\block_labels_7_10_15_17_20, replace


//////

//block data with distributed income
use data\labels\generated_files\demos_inc_block_00, clear

*applying crosswalk weight to 2000 blocks, to get to 2010 blocks
merge 1:m gisjoin using data\labels\source_files\nhgis_blk2000_blk2010_gj, nogen keep(match)
drop gisjoin //this is 2000 gisjoin
rename gjoin2010 gisjoin

local indices "white black hispanic workage female groupshare"
foreach v in `indices' {
	replace `v' = `v'*pop
}

local blockvars "pop inc white black hispanic workage female pshare groupshare"

foreach v of varlist `blockvars' {
	replace `v' = `v'*weight
}

//collapsing from full crosswalk to 2010 blocks
collapse (sum) `blockvars' weight, by(gisjoin)

//this is from JAN20_cleaning_block_labels.do
merge 1:1 gisjoin using data\labels\generated_files\block_labels_7_10_15_17_20, nogen keep(match)


foreach v of varlist pop inc white black hispanic workage female pshare groupshare emp_* {
	rename `v' `v'_00
}
drop blockemp cntyemp pshare_00

//getting popshare
gen gisjoin_bg = substr(gisjoin,1,15)
bysort gisjoin_bg: egen pop_bg_00 = total(pop_00)
by gisjoin_bg: egen inc_bg_00 = total(inc_00)


merge 1:1 gisjoin using data\labels\generated_files\block_areas10, nogen keep(match)

preserve

collapse (firstnm) pop_bg_00 (sum) shape_area, by(gisjoin_bg)
gen pd = pop / shape_area
gen negpopd = -pd
gen negpop = -pop
sort negpopd negpop
gen sumpop = sum(pop) 
sort negpopd negpop
egen tpop = total(pop)
sort negpopd negpop
gen popshare_00 = sumpop/tpop
keep gisjoin_bg popshare
tempfile popshare
save `popshare'
restore

merge m:1 gisjoin_bg using `popshare', nogen keep(match)

drop weight
order gisjoin gisjoin_bg shape_area pop_* inc_* popshare_00 groupshare_00 white_00 black_00 hispanic_00 workage_00 female_00 emp_sec1_00 emp_sec2_00 emp_sec3_00 emp_sec4_00 emp_sec5_00 emp_sec6_00 emp_sec7_00 emp_sec8_00 emp_sec9_00 emp_sec10_00 emp_sec11_00 emp_sec12_00 emp_sec13_00 emp_sec14_00 emp_sec15_00 emp_sec16_00 emp_sec17_00 emp_sec18_00 emp_sec19_00 emp_sec20_00 emp_bus_serv_00 emp_nonbus_serv_00 emp_prod_00 emp_bus_serv_cnty_00 emp_nonbus_serv_cnty_00 emp_prod_cnty_00

foreach v of varlist emp_sec1_00 emp_sec2_00 emp_sec3_00 emp_sec4_00 emp_sec5_00 emp_sec6_00 emp_sec7_00 emp_sec8_00 emp_sec9_00 emp_sec10_00 emp_sec11_00 emp_sec12_00 emp_sec13_00 emp_sec14_00 emp_sec15_00 emp_sec16_00 emp_sec17_00 emp_sec18_00 emp_sec19_00 emp_sec20_00 emp_bus_serv_00 emp_nonbus_serv_00 emp_prod_00  {
	replace `v' = `v'*pop_00
}

bysort gisjoin_bg: egen bg_area = total(shape_area)
rename shape_area block_area

*****************************************
save data\labels\generated_files\block_labels_cw, replace
*****************************************


gen gisjoin_cnty = substr(gisjoin,1,8)

foreach v in pop_00 pop_10 inc_00 inc_10 {
	replace `v' = exp(`v')
}

collapse (sum) block_area pop_00 pop_10 inc_00 inc_10, by(gisjoin_cnty)

rename block_area cnty_area
rename pop* pop_cnty_*
rename inc* inc_cnty_*

save data\labels\generated_files\cnty_areas.dta, replace
}





