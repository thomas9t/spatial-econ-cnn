
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


cd "...set base working directory here..."

capture mkdir results
capture mkdir data\applications

//Script to clean prediction data and produce all tex files containing R2 figures for tables in manuscript
do "code\produce_results\replicate draft r2 stats.do"

//Script to produce graphs in manuscript
do "code\produce_results\replicate draft figures.do"

//Script to export cleaned prediction data for applications using our outcomes
do "code\produce_results\generate prediction panel.do"




