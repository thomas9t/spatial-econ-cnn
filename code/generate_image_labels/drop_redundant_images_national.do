

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


//this script would likely take about 1-2 days to rerun

foreach size in "national_small" "national_large" "mw_highres" {
    
	//this list of centroids is the lat/lng for each image in the TFRecord files exported from google earth engine
	use data\labels\generated_files\allpredpts_`size'_addon, clear

	count
	sort img_id


	quietly {

	local i = 1

	while `i' < _N {
		** if i'm just above another image, drop me
		if ceil(`i'/1000) == `i'/1000 noisily di "obs `i'" 
		count if (lat<lat[`i']) & (lat>lat[`i']-0.012) & (lng>=lng[`i']-.01) & (lng<=lng[`i']+.01)
		if r(N)>0 drop in `i'
		else local i = `i'+1
	}
	}

	sort img_id
	count
	local i = 2
	quietly{
	while `i'<_N {
		if lng[`i']-lng[`i'-1]<.012 & lat[`i']==lat[`i'-1] drop in `i'
		else local i = `i'+1
	}
	}
	count


	export delimited using data\labels\generated_files\valid_imgs_rowcoltrim_`size'_addon.csv, replace
	save data\labels\generated_files\valid_imgs_rowcoltrim_`size'_addon, replace
}



