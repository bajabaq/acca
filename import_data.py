
import configparser
import os
import sys
import csv
import sqlite3
import hashlib

#------------------------------------------------------------------------------
#get digest of file using given hasher (md5, sha256, etc)
#------------------------------------------------------------------------------
def hashfile(afile, hasher, blocksize=65536):
    fh = open(afile, 'rb')
    buf = fh.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = fh.read(blocksize)
    fh.close()
    return hasher.hexdigest()

#------------------------------------------------------------------------------
#check filename hash value matches that saved in the settings file
#returns True if matches, the hash if it does not
#------------------------------------------------------------------------------    
def check_hash(settings, section, filename):
    bname = os.path.basename(filename)
    saved_digest256 = settings.get(section, bname)    
    digest256       = hashfile(filename, hashlib.sha256())
    
    #print(filename)
    #print(saved_digest256)
    #print(digest256)
    
    result = False
    if saved_digest256 == digest256:
        result = True
    else:
        result = digest256
    #endif
    #print(result)
    return result
#endif

#------------------------------------------------------------------------------
#Update the settings file with the latest hash
#------------------------------------------------------------------------------
def update_hash(settings, settings_file, section, item, value):
    print("...updating hash in config file for " + item + " ...")
    settings.set(section, item, value)    
    with open(settings_file,'w') as configfile:
            settings.write(configfile)
    #endwith            
#enddef


#------------------------------------------------------------------------------
#Get the SQL to create the table in the database
#------------------------------------------------------------------------------
def get_create_SQL(file):
    if file == 'noise.csv':
        SQL = """CREATE TABLE noise (
                 location text, 
                 application text, 
                 nc_level_min float,
                 nc_level_max float,
                 maximum_velocity float
                 );
              """
    elif file == 'air_term_mfg_specs.csv':
        SQL = """CREATE TABLE air_term_mfg_specs ( 
                    model text,
                    type  text,
                    duct_dim_in  text,
                    duct_area_sqft float,
                    duct_area_type text,
                    throw_direction text,
                    velocity_fpm float,
                    velocity_type text,
                    pressure_loss float,
                    terminal_velocity float,
                    cfm float,
                    spread float,
                    throw float,
                    ak float,
                    nc float
                    );                 
              """
    elif file == 'outdoor_design_cond.csv':
        SQL = """CREATE TABLE outdoor_design_cond ( 
                    state text,
                    city  text,
                    elevation float,
                    latitude float,
                    heating_99per_db float,
                    cooling_1per_db float,
                    concident_wb float, 
                    design_grains_55per_rh float,
                    design_grains_50per_rh float,
                    design_grains_45per_rh float,
                    daily_range text
                    );                 
              """
    elif file == 'altitude_info.csv':
        SQL = """CREATE TABLE altitude_info ( 
                    altitude float,
                    acf float,
                    lbpercf float
                    );
              """
    elif file == 'latitude_slm.csv':
        SQL = """CREATE TABLE latitude_slm ( 
                    north_latitude float,
                    direction text,
                    slm float                    
                    );
              """
    elif file == 'fenestration_performance.csv':
        SQL = """CREATE TABLE fenestration_performance (
                    construction_number text,
                    frame_type  text,
                    u float,
                    shgc float                    
                    );
              """
    elif file == 'cooling_htm.csv':
        SQL = """CREATE TABLE cooling_htm (
                    glass_type text,
                    shade text,
                    num_panes_thick text,
                    direction text,
                    ctd float,
                    htm float
                    );
              """
    elif file == 'opaque_panel_performance_cltd.csv':
        SQL = """CREATE TABLE opaque_panel_performance_cltd (
                    construction_number text,
                    ctd float,
                    daily_range text,
                    cltd float,
                    group_num text,
                    construction text
                    );
              """
    elif file == 'opaque_panel_performance_u.csv':
        SQL = """CREATE TABLE opaque_panel_performance_u (
                    construction_number text,
                    u_val float,
                    group_num text
                    );
              """
    elif file == 'opaque_panel_performance_ptdh.csv':
        SQL = """CREATE TABLE opaque_panel_performance_ptdh (
                    construction_number text,
                    htd float,
                    ptdh float
                    );
              """
    elif file == 'duct_load_default_surface_area.csv':
        SQL = """CREATE TABLE duct_load_default_surface_area (
                    construction_number text,
                    floor_area float,
                    supply float,
                    return float
                    );
              """
    elif file == 'duct_load_surface_area_factors.csv':
        SQL = """CREATE TABLE duct_load_surface_area_factors (
                    construction_number text,
                    leakage_type text,
                    leakage float,
                    k float
                    );
              """
    elif file == 'duct_load_blg.csv':
        SQL = """CREATE TABLE duct_load_blg (
                    construction_number text,
                    grains float,
                    floor_area float,
                    blg float
                    );
              """
    elif file == 'duct_load_bsgf.csv':
        SQL = """CREATE TABLE duct_load_bsgf (
                    construction_number text,
                    oat float,
                    floor_area float,
                    bsgf float
                    );
              """
    elif file == 'duct_load_bhlf.csv':
        SQL = """CREATE TABLE duct_load_bhlf (
                    construction_number text,
                    oat float,
                    floor_area float,
                    bhlf float
                    );
              """
    elif file == 'duct_load_rval_correction.csv':
        SQL = """CREATE TABLE duct_load_rval_correction (
                    construction_number text,
                    rval float,
                    bhlf_correction float,
                    bsgf_correction float
                    );
              """
    elif file == 'duct_load_leakage.csv':
        SQL = """CREATE TABLE duct_load_leakage (
                    construction_number text,
                    leakage text,
                    rval float,
                    heat_loss_correction float,
                    sensible_correction float,
                    latent_correction float
                    );
              """
    elif file == 'air_change_value.csv':
        SQL = """CREATE TABLE air_change_value (
                    construction text,
                    floor_area float,
                    ach_heating float,
                    ach_cooling float
                    );
              """
    elif file == 'fireplace_infiltration.csv':
        SQL = """CREATE TABLE fireplace_infiltration (
                    construction text,
                    infiltration float
                    );
              """   
    #endif
              
    return SQL
#enddef

#------------------------------------------------------------------------------
#Get the SQL to load the data to the database
#------------------------------------------------------------------------------
def get_load_SQL(file):
    if file == 'noise.csv':
        SQL = """INSERT INTO noise (location,   application,  nc_level_min,  nc_level_max,  maximum_velocity)
                 VALUES            (:location, :application, :nc_level_min, :nc_level_max, :maximum_velocity)
              """
    elif file == 'air_term_mfg_specs.csv':
        SQL = """INSERT INTO air_term_mfg_specs ( model,  type,  duct_dim_in, duct_area_sqft, duct_area_type, throw_direction,  velocity_fpm, velocity_type, pressure_loss,  terminal_velocity,  cfm,  spread,  throw,  ak,  nc)
                 VALUES                         (:model, :type, :duct_dim_in, :duct_area_sqft, :duct_area_type, :throw_direction, :velocity_fpm, :velocity_type, :pressure_loss, :terminal_velocity, :cfm, :spread, :throw, :ak, :nc)
              """
    elif file == 'outdoor_design_cond.csv':
        SQL = """INSERT INTO outdoor_design_cond (  state,  city,  elevation,  latitude,  heating_99per_db,  cooling_1per_db,  concident_wb,  design_grains_55per_rh,  design_grains_50per_rh,  design_grains_45per_rh,  daily_range)
                 VALUES                          ( :state, :city, :elevation, :latitude, :heating_99per_db, :cooling_1per_db, :concident_wb, :design_grains_55per_rh, :design_grains_50per_rh, :design_grains_45per_rh, :daily_range)
              """
    elif file == 'altitude_info.csv':
        SQL = """INSERT INTO altitude_info (  altitude,  acf,  lbpercf)
                 VALUES                    ( :altitude, :acf, :lbpercf)
              """
    elif file == 'latitude_slm.csv':
        SQL = """INSERT INTO latitude_slm (  north_latitude,  direction,  slm)
                 VALUES                   ( :north_latitude, :direction, :slm)
              """
    elif file == 'fenestration_performance.csv':
        SQL = """INSERT INTO fenestration_performance (  construction_number,  frame_type,  u,  shgc)
                 VALUES                               ( :construction_number, :frame_type, :u, :shgc)
              """
    elif file == 'cooling_htm.csv':
        SQL = """INSERT INTO cooling_htm (  glass_type,  shade,  num_panes_thick,  direction,  ctd,  htm)
                 VALUES                  ( :glass_type, :shade, :num_panes_thick, :direction, :ctd, :htm)
              """
    elif file == 'opaque_panel_performance_cltd.csv':
        SQL = """INSERT INTO opaque_panel_performance_cltd (  construction_number,  ctd,  daily_range,  cltd,  group_num,  construction)
                 VALUES                                    ( :construction_number, :ctd, :daily_range, :cltd, :group_num, :construction)
              """
    elif file == 'opaque_panel_performance_u.csv':
        SQL = """INSERT INTO opaque_panel_performance_u (  construction_number,  u_val,  group_num)
                 VALUES                                 ( :construction_number, :u_val, :group_num)
              """
    elif file == 'opaque_panel_performance_ptdh.csv':
        SQL = """INSERT INTO opaque_panel_performance_ptdh (  construction_number,  htd,  ptdh)
                 VALUES                                    ( :construction_number, :htd, :ptdh)
              """
    elif file == 'duct_load_default_surface_area.csv':
        SQL = """INSERT INTO duct_load_default_surface_area (  construction_number,  floor_area,  supply,  return)
                 VALUES                                     ( :construction_number, :floor_area, :supply, :return)
              """
    elif file == 'duct_load_surface_area_factors.csv':
        SQL = """INSERT INTO duct_load_surface_area_factors (  construction_number,  leakage_type,  leakage,  k)
                 VALUES                                     ( :construction_number, :leakage_type, :leakage, :k)
              """
    elif file == 'duct_load_blg.csv':
        SQL = """INSERT INTO duct_load_blg (  construction_number,  grains,  floor_area,  blg)
                 VALUES                    ( :construction_number, :grains, :floor_area, :blg)
              """
    elif file == 'duct_load_bsgf.csv':
        SQL = """INSERT INTO duct_load_bsgf (  construction_number,  oat,  floor_area,  bsgf)
                 VALUES                     ( :construction_number, :oat, :floor_area, :bsgf)
              """
    elif file == 'duct_load_bhlf.csv':
        SQL = """INSERT INTO duct_load_bhlf (  construction_number,  oat,  floor_area,  bhlf)
                 VALUES                     ( :construction_number, :oat, :floor_area, :bhlf)
              """
    elif file == 'duct_load_rval_correction.csv':
        SQL = """INSERT INTO duct_load_rval_correction (  construction_number,  rval,  bhlf_correction,  bsgf_correction)
                 VALUES                                ( :construction_number, :rval, :bhlf_correction, :bsgf_correction)
              """
    elif file == 'duct_load_leakage.csv':
        SQL = """INSERT INTO duct_load_leakage (  construction_number,  leakage,  rval,  heat_loss_correction,  sensible_correction ,  latent_correction)
                 VALUES                        ( :construction_number, :leakage, :rval, :heat_loss_correction, :sensible_correction , :latent_correction)
              """
    elif file == 'fireplace_infiltration.csv':
        SQL = """INSERT INTO fireplace_infiltration (  construction,  infiltration)
                 VALUES                             ( :construction, :infiltration)
              """
    elif file == 'air_change_value.csv':
        SQL = """INSERT INTO air_change_value (  construction,  floor_area, ach_heating, ach_cooling)
                 VALUES                       ( :construction, :floor_area, :ach_heating, :ach_cooling)
              """
        
    #endif
    
    return SQL
#enddef

#------------------------------------------------------------------------------
#Drop table and reload it to the database
#------------------------------------------------------------------------------
def reload_csv(settings, settings_file, file, result):
    print("Updating " + file + "...")
    
    table = os.path.splitext(file)[0]
    
    db_filename = get_db_filename(settings)
    conn = sqlite3.connect(db_filename)
    
    print("...dropping the table...")
    SQL = 'DROP TABLE IF EXISTS ' + table + ';'
    conn.executescript(SQL)
    
    print("...creating the table...")
    SQL = get_create_SQL(file)
    conn.executescript(SQL)
    
    print("...loading the table...")
    data_filename = get_data_filename(settings,file)
    with open(data_filename, 'rt') as csv_file:
        csv_reader    = csv.DictReader(csv_file)
        SQL           = get_load_SQL(file)        
        conn.executemany(SQL, csv_reader)    
    #endwith
    conn.commit()
    
    conn.close()
        
    update_hash(settings, settings_file, 'data_hashes', file, result)            
    print("...Done")
#enddef

#------------------------------------------------------------------------------
#Check if the data has changed
#------------------------------------------------------------------------------
def check_data(settings, settings_file):
    print("Checking each data file listed in the settings file...")
    data_path = settings.get('system', 'data_dir')
    data_file_hashes = dict(settings.items('data_hashes'))
    for file,hash in data_file_hashes.items():
        fname = os.path.abspath(data_path + '/' + file)        
        result = check_hash(settings,'data_hashes',fname)        
        if result == True:
            print("OK " + file)
        else:     
            #TODO make this interactive
            print("Data file differs from previous...Do you wish to update the database (Y/N)? [Y]")
            response = "y"
            if response == "y":
                reload_csv(settings, settings_file, file, result)
            #endif
        #endif      
    #endfor   
    print("...checking finished")
    return
#enddef

#------------------------------------------------------------------------------
#Get data filename
#------------------------------------------------------------------------------
def get_data_filename(settings,data):
    path          = settings.get('system','data_dir')    
    data_filename = os.path.abspath(path + '/' + data)
    return data_filename
#enddef

#------------------------------------------------------------------------------
#Get database filename
#this might should be in own module vs copy in each source file
#------------------------------------------------------------------------------
def get_db_filename(settings):
    db_path         = settings.get('system','data_dir')
    db_filename_org = settings.get('system','database')
    db_filename     = os.path.abspath(db_path + '/' + db_filename_org)
    return db_filename
#enddef

#------------------------------------------------------------------------------
#See if database exists, if not then touch it, if so do nothing
#------------------------------------------------------------------------------
def check_database(settings):
    db_filename = get_db_filename(settings)    
    db_exists   = os.path.exists(db_filename)

    if not db_exists:    
        print("Touching database")
        conn = sqlite3.connect(db_filename)
        conn.close()
    else:
        print("Database exists - doing nothing")
    #endif
    
    return
#enddef

#------------------------------------------------------------------------------
# Main Execution point
#------------------------------------------------------------------------------
if __name__ == '__main__':

    #read the system settings file (maybe should be in own module)
    settings = configparser.ConfigParser()
    settings_file = os.path.abspath('system_settings.txt')
    settings.read(settings_file)

    check_database(settings)
        
    #check the data files are up to date(listed in the system_settings file)
    check_data(settings, settings_file)
        
    print("Done")

#endif
