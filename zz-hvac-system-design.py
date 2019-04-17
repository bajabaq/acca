#------------------------------------------------------------------------------
# Top level program for designing an HVAC system based on ACCA manuals
# TSW-5/20/2016
# I would like this program to fall under the GNU-GPL, but not sure if 
# the manual's copyright would restrict that....
#------------------------------------------------------------------------------
import sys

from site_survey import site_survey
from load_calc import load_calc
from equipment_selection import equipment_selection
from air_distribution import air_distribution
from duct_design import duct_design
from design_presentation import system_presentation


#------------------------------------------------------------------------------
# MAIN program
#------------------------------------------------------------------------------
print("This is the main program for designing a residential HVAC system")

print("Doing site_survey...")
project = site_survey() #project is a reference to the project file
print("Done")

print("Doing load calculation...")
load_calc(project)  #manual J / Jae
print("Done")

print("Doing equipment selection...")
equipment_selection(project)  #manual S
print("Done")

print("Doing air distribution...")
air_distribution(project)  #manual T
print("Done")

print("Doing duct design...")
duct_design(project)  #manual D
print("Done")

print("Presenting final report...")
system_presentation(project) 
print("Done")

sys.exit()



