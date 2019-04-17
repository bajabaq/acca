
import pytest

import configparser
import os

from .. import hvac_database

 
def test_hvac_database():
    #read the system settings file (maybe should be in own module - along w/ get_database name)
    settings      = configparser.ConfigParser()
    settings_file = os.path.abspath('system_settings.txt')
    settings.read(settings_file)
    assert hvac_database.get_db_filename(settings) == os.path.relpath(os.path.join(os.getcwd(),'data/acca3.sqlite'))

def test_do_query():
    #read the system settings file (maybe should be in own module - along w/ get_database name)
    settings      = configparser.ConfigParser()
    settings_file = os.path.abspath('system_settings.txt')
    settings.read(settings_file)    
    SQL = """SELECT latitude FROM outdoor_design_cond WHERE state = ? AND city = ?"""    
    SQL_vars = ('texas', 'houston ap',)    
    assert hvac_database.do_query(settings, SQL, SQL_vars) == [(29.0,)]
