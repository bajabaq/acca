
import pytest

import configparser
import os

from .. import load_calc_wksht_e

#maybe can delete this - or expand for other projects
def get_test_results(project_name, settings, project):
    t_results = {}
    if project_name == 'Vatilo Residence':
        a_results = {
            'project'          :'Vatilo Residence',
            'city'             :'houston ap',
            'state'            :'texas',
            'elevation'        :96,
            'latitude'         :29,         
            'indoor_heating_db':70,
            'indoor_heating_rh':'',
            'indoor_cooling_db':75,
            'indoor_cooling_rh':50,
            'outdoor_99per_db' :31,
            'outdoor_1per_db'  :94,  
            'grains_diff'      :51,      
            'daily_range'      :'m',      
            'htd'              :39,              
            'ctd'              :19,
            'acf'              :0.99712,
            'air_den'          :0.074712,
        }
         
        t_results = {
            'settings'            : settings,
            'project'             : project,
            'floor_area_heating'  : 1200,
            'floor_area_cooling'  : 1200,
            'conditioned_ag_vol_h': 9600,
            'conditioned_ag_vol_c': 9600,
            'num_bedrooms'        : 2,
            'num_occupants'       : 3,
            'num_fireplaces'      : 0,
            'burner_capacity'     : 0,
            'htd'                 : 39,
            'ctd'                 : 19,
            'grains_difference'   : 51,
            'acf'                 : 1.00,
            'envelope'            : 'average',
            'envelope_ach_heating': 0.45,
            'envelope_ach_cooling': 0.23,
            'infiltration_heating': 72,
            'infiltration_cooling': 37,
            'infiltration_load_heating': 3089,
            'sens_infil_load_cooling'  : 769,
            'lat_infil_load_cooling'   : 1276,
            'diff_fresh_air_infil_heat': -12,
            'diff_fresh_air_infil_cool': 23,
            'eng_vent'                 : 23,
        }
    else:
        a_results = {}
        t_results = {}
    #endif
    
    return a_results, t_results
#enddef

def get_settings():
    #read the system settings file (maybe should be in own module - along w/ get_database name)
    settings      = configparser.ConfigParser()
    settings_file = os.path.abspath('system_settings.txt')
    settings.read(settings_file)
    return settings
#enddef


def test_get_oa_ach():
    assert load_calc_wksht_e.get_oa_ach(60) == 0.35


def test_get_ach():
    settings = get_settings()
    assert load_calc_wksht_e.get_ach(settings, 'ach_heating', 'tight', 0)    == 0.21
    assert load_calc_wksht_e.get_ach(settings, 'ach_heating', 'tight', 900)  == 0.21
    assert load_calc_wksht_e.get_ach(settings, 'ach_heating', 'tight', 901)  == 0.16
    assert load_calc_wksht_e.get_ach(settings, 'ach_heating', 'tight', 902)  == 0.16
    assert load_calc_wksht_e.get_ach(settings, 'ach_heating', 'tight', 1500) == 0.16
    assert load_calc_wksht_e.get_ach(settings, 'ach_heating', 'tight', 1501) == 0.14
    assert load_calc_wksht_e.get_ach(settings, 'ach_heating', 'tight', 1502) == 0.14
    assert load_calc_wksht_e.get_ach(settings, 'ach_heating', 'tight', 2000) == 0.14
    assert load_calc_wksht_e.get_ach(settings, 'ach_heating', 'tight', 2001) == 0.11
    assert load_calc_wksht_e.get_ach(settings, 'ach_heating', 'tight', 2999) == 0.11
    assert load_calc_wksht_e.get_ach(settings, 'ach_heating', 'tight', 3000) == 0.10
    assert load_calc_wksht_e.get_ach(settings, 'ach_heating', 'tight', 3001) == 0.10



def test_load_calc_wksht_e():
    settings = get_settings()
    
    project = configparser.ConfigParser()
    project_file = os.path.abspath('../projects/man_j_sec7/man_j_sec7.txt') #vatilo residence - block load
    project.read(project_file)
    
    a_results, t_results = get_test_results('Vatilo Residence', settings, project) 
    pass
    #come write the fix for this
    #assert load_calc_wksht_e.worksheet_e(settings, project, a_results) == t_results
    
