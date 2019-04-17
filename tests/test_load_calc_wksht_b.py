
import pytest

import configparser
import os

from .. import load_calc_wksht_b

#maybe can delete this - or expand for other projects
def get_test_results(project_name):
    t_results = {}
    if project_name == 'Vatilo Residence':
         t_results = {
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
               'air_den'          :0.074712
               }     
    else:
        t_results = {}
    #endif
    return t_results
#enddef

def get_settings():
    #read the system settings file (this should be in own module - along w/ get_database name)
    settings      = configparser.ConfigParser()
    settings_file = os.path.abspath('system_settings.txt')
    settings.read(settings_file)
    return settings
#enddef
   

def test_get_fenestration_performance():
    settings = get_settings()
    construction_num = '1A-c'
    frame_type = 'm'
    assert load_calc_wksht_b.get_fenestration_performance(settings, construction_num, frame_type) == (1.27,0.75)

def test_get_htm_adjustment_heating():
    window_door_type = 'default'
    assert load_calc_wksht_b.get_htm_adjustment_heating(window_door_type) == 1
    
def test_get_htm_cooling():
    construction_num = '1A-c'
    internal_shade   = 'none'
    num_panes_thick  = 2
    direction        = 'E'
    ctd              = 33
    settings         = get_settings()
    assert load_calc_wksht_b.get_htm_cooling(construction_num, internal_shade, num_panes_thick, direction, ctd, settings) == 81

def test_get_htm_adjustment_cooling():
    window_door_type = 'default'
    insect_screen    = 'none'
    assert load_calc_wksht_b.get_htm_adjustment_cooling(window_door_type, insect_screen) == 1

def test_get_slm():
    settings = get_settings()
    assert load_calc_wksht_b.get_slm(settings, 30, 'W') == 0.83
    assert load_calc_wksht_b.get_slm(settings, 30, 'E') == 0.83
   
   
def test_get_win():
    settings = get_settings()
    pass
    #write this test later
    #assert load_calc_wksht_b.get_win(htd, ctd, latitude, direction, win_type_section, settings, project) == win_res
    



    
def test_load_calc_wksht_b():
    settings = get_settings()
    
    project = configparser.ConfigParser()
    project_file = os.path.abspath('projects/man_j_sec7/man_j_sec7.txt') #vatilo residence - block load
    project.read(project_file)
    a_results = {
               'project'          :'Vatilo Residence',
               'city'             :'houston ap',
               'state'            :'texas',
               'elevation'        :96.0,
               'latitude'         :29.0,         
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
               'air_den'          :0.074712
               }

    t_results = {
               'project'          :'Vatilo Residence',
               'city'             :'houston ap',
               'state'            :'texas',
               'elevation'        :96.0,
               'latitude'         :29.0,         
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
               'air_den'          :0.074712
               }
    
    
    pass
    #write this test correctly later
    #assert load_calc_wksht_b.worksheet_b(settings, project, a_results) == t_results
    
