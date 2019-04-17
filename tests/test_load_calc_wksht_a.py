
import configparser
import os

from .. import load_calc_wksht_a

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
    #read the system settings file (maybe should be in own module - along w/ get_database name)
    settings      = configparser.ConfigParser()
    settings_file = os.path.abspath('system_settings.txt')
    settings.read(settings_file)
    return settings
#enddef

def test_get_coil_climate():
    assert load_calc_wksht_a.get_coil_climate('texas', 'houston ap') == 'wet'
    assert load_calc_wksht_a.get_coil_climate('florida', 'miami')    == 'super_wet'
    assert load_calc_wksht_a.get_coil_climate('arizona', 'phoenix')  == 'dry'

def test_get_humidity_info():
    assert load_calc_wksht_a.get_humidity_info('wet'      , 55, 50, 45) == (50, 50)
    assert load_calc_wksht_a.get_humidity_info('super_wet', 55, 50, 45) == (55, 55)
    assert load_calc_wksht_a.get_humidity_info('dry'      , 55, 50, 45) == (45, 45)
    
    
def test_get_altitude_info():
    settings = get_settings()
    assert load_calc_wksht_a.get_altitude_info(settings, 96.0)  == (0.99712, 0.074712) #interpolate    
    assert load_calc_wksht_a.get_altitude_info(settings, -279)  == (1.00837, 0.075837) #extrapolate backward (death valley)
    assert load_calc_wksht_a.get_altitude_info(settings, 20310) == (0.38070, 0.031380) #extrapolate forward  (denali)
    

def test_load_calc_wksht_a():
    settings = get_settings()
    
    project = configparser.ConfigParser()
    project_file = os.path.abspath('projects/man_j_sec7/man_j_sec7.txt') #vatilo residence - block load
    project.read(project_file)
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
    
    assert load_calc_wksht_a.worksheet_a(settings, project) == t_results
    