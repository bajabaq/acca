import configparser
import os
import math
import sqlite3
import sys

from hvac_database import get_db_filename, do_query
from hvac_math import interpolate_val

#------------------------------------------------------------------------------
#air velocity reduces exponentially with distance - throw, unknown is the factor
#FPM = FaceFPM * exp ( -F * D) 
#D is distance and F is factor (typically between 0.1 - 0.001)
#maybe can estimate from manufacturer information
#Throw = -ln(FPM/FPM0)/B
#FPM0 = face FPM
#
#max_drop = ceiling_heigh - 6'
#min_throw = distance to wall - 2'
#occupied space = 2' from each wall and 6' to ceiling
#
#------------------------------------------------------------------------------

#clean this up

def get_noise_criteria(settings, project_location, project_application):
    db_filename = get_db_filename(settings)
        
    man_t_db = db_filename
    table    = 'noise'

    conn = sqlite3.connect(man_t_db)
    c = conn.cursor()
    c.execute('SELECT nc_level_max,maximum_velocity FROM {tn} WHERE {cn1}="{val1}" AND {cn2}="{val2}"'.\
    format(tn=table, cn1='location', cn2='application', val1=project_location, val2=project_application))
    matching_row = c.fetchall()
    conn.close()
    if len(matching_row) != 1:
        print("Error, either 0 or >1 row found matching criteria in get_noise_criteria")
        sys.exit()
    #endif
    
    noise_criteria = matching_row[0]
    #print(noise_criteria[0], noise_criteria[1])

    return noise_criteria
#enddef

#------------------------------------------------------------------------------
# Get the Throw, FPM, .... so can look up and get outlet
#------------------------------------------------------------------------------
def get_supply_specs(project, room, supply_info, max_nc, max_fpm):
    throw     = 0
    spread    = 0
    face_velo = 0

    supply_location = supply_info[0]
    supply_x = float(supply_info[1])
    supply_y = float(supply_info[2])
    supply_z = float(supply_info[3])
                
    print("Supply Location is: " + supply_location + " (" + str(supply_x) + ", " + str(supply_y)  + ", " + str(supply_z) + ")"
    
    #this assumes all rooms are cuboid
    room_x = float(project.get(room, 'x'))  # this may need to be better identified (so know where outlets go)
    room_y = float(project.get(room, 'y'))  # this may need to be better identified
    room_z = float(project.get(room, 'z'))  # this may need to be better identified
    
    #check that supply location is within room
    if ((supply_y >= room_y) or (supply_x >= room_x) or (supply_z >= room_z)):
        print("Error your supply locations are outside of the room boundaries")
        sys.exit()
    #endif
        
    #hack b/c now doing supply 1 at a time - fix this
    num_supply_terminals = 1 
        
    if (supply_location == 'floor' or supply_location == 'baseboard' or supply_location == 'low sidewall'):
        throw_y1 = (room_y - supply_y)        
        throw_y2 = (supply_y)        
        throw_x1 = (room_x - supply_x)
        throw_x2 = (supply_x)
        
        if ((throw_y1 > 2 and throw_y2 > 2) and (throw_x1 > 2 and throw_x2 > 2)):
            print("supply location in occupied zone, this is odd, check your design (or this code...)"
            sys.exit()
        #endif
        
        #throw direction = max distance to wall
        throw_y = max(throw_y1, throw_y2)
        throw_x = max(throw_x1, throw_x2)
        
        if throw_y == throw_x:
            print("outlet is equidistant from x and y walls - don't know what to do..."
            sys.exit()
        #endif        
        #print(throw_short
        
        if throw_short == throw_y1:
            throw = throw_y2
            print("throw is in the y direction")
            print("spread is in the x direction")
            
            spread = room_x / num_supply_terminals
            #print(spread)
            
            #do something here to determine spread vs room_size vs throw account for multiple outlets, etc
            
            spread_x1     = throw_x1
            min_spread_x1 = spread_x1 - 2
            
            spread_x2     = throw_x2
            min_spread_x2 = spread_x2 - 2
            
            min_spread = min(min_spread_x1, min_spread_x2) * 2
            max_spread = max(spread_x1, spread_x2) * 2
                        
        else: #throw_short == throw_x1
            throw = throw_x2
            print("throw is in the x direction"
            print("spread is in the y direction"
            
            spread = room_y / num_supply_terminals
            #print(spread
            
            spread_y1     = throw_y1
            min_spread_y1 = spread_y1 - 2
            
            spread_y2     = throw_y2
            min_spread_y2 = spread_y2 - 2
            
            min_spread = min(min_spread_y1, min_spread_y2) * 2
            max_spread = max(spread_y1, spread_y2) * 2
            
        #endif
        min_spread = math.floor(min_spread)
        max_spread = math.ceil(max_spread)
        
        min_throw = math.floor(throw - 2) #minimum throw is within the occupied zone (2 ft from wall)
        max_throw = math.ceil(throw + 1) #max throw slightly greater than ceiling height - according to Sec 5 - (conflics w/ 10-8) - unclear
        #print(throw, min_throw)
        #print(min_spread, max_spread)
        
        face_velo = 600 #or 700 - section 10.8 is unclear
        tdiff     = 20
        msg = "For this room, you need to pick an outlet that has a \n"
        msg = msg + "Throw         = " + str(min_throw) + " - " + str(max_throw) + "\n"
        msg = msg + "Spread        = " + str(min_spread) + " - " + str(max_spread) + "\n"
        msg = msg + "Face Velocity = " + str(face_velo) + "\n"
        print(msg
        
    
    #floor/baseboard/low sidewall (diffusers go up, baseboard/sidewall goes out?
    #section 5; 10-8
    #throw = 4-6 heat 6-8 cool ft
    #spread = wider is better - see high wall rules for good guidelines - TSW thinks
    #face velo = < 600, max 700
    #temp diff = 75F heating 20F cooling
    #pressure drop = note for Manual D


    #--------------------------------------------------------------------------
    #ceiling
    #section 4; 10-10
    
    #what is temperature difference between room and supply air
    #throw = 100 fpm (isothermal) = 50 fpm (20 TD)   
    #        360 degree diffusers, throw = distance to nearest wall OR 1/2 distance to adjacent terminal - use 100 fpm 
    #        directional diffusers - thow = 0.75-1.2 to nearest wall (cooling) or 1.0 - 1.2 (heating) - use 100 fpm
    #air drop - not an issue if mounted next to ceiling, max_drop = (celing - 6')
    #spread = wider is better
    #neck velo = < 700 - see 10-6 table for noise issues corresponding to FPM
    
    #temp diff = see 4-10 - 10-25F cooling - 25F - ok for diretional diffusers and 20F for circular; typically heating supply air ~=100F
    #
    #pressure drop = note for Manual D    
    #--------------------------------------------------------------------------
    elif (supply_location == 'ceiling'):
        
        if (room_z - supply_z) > 0:  
            print("you need to worry about air_drop"
        #endif
        
        throw_y1 = (room_y - supply_y)        
        throw_y2 = (supply_y)        
        throw_x1 = (room_x - supply_x)
        throw_x2 = (supply_x)
        
        max_throw = max(throw_y1, throw_y2, throw_x1, throw_x2)
        min_throw = min(throw_y1, throw_y2, throw_x1, throw_x2)
        
        print("Need throw of " + str(min_throw) + "  @ 100fpm"
        print("Need throw of " + str(max_throw) + " @  50fpm"
        
        spread    = 0 #means non directional or 360degrees
        face_velo = max_fpm
        
            
    
    #high sidewall    
    #section 3; 10-13
    #throw distance = 80-120% of distance to opposoite (hopefully outside) wall
    #terminal velocity = 50-100 fpm
    
    #throw = 100 fpm isothermal 
    #        cooling throw = 0.75-1.2 OK - 1.0 -1.2 better use 100 fpm
    #air drop - if data not available, refer to generic drop graphs see 10-13
    #spread = wider is better - not exceed space between outlet center-lines  or adjacent walls
    #sidewall outlet spacing so air streams do not merge until air has been project to 50% of throw
    
    #face velo = < 600, 700 max - see 10-6 table for noise issues corresponding to FPM
    
    #temp diff = see 4-10 - 20F cooling 20-25F heating
    #
    #pressure drop = note for Manual D
    elif (supply_location == 'high sidewall'):
        print(supply_location
    else:
        print("Error - SUPPLY_LOCATION is not known (floor, baseboard, low sidewall, ceiling, high sidewall)"
        sys.exit()
    #endif
    
    supply_specs = [throw, spread, face_velo]
    
    return supply_specs
#enddef

            
def get_model_specs(settings, value, params):
    SQL = "SELECT cfm, velocity_fpm, velocity_type, throw, pressure_loss, spread FROM air_term_mfg_specs WHERE"
    if value == "upper":
        SQL = SQL + """ model = ? AND duct_dim_in = ? AND ? <= cfm ORDER BY cfm ASC LIMIT 1"""
    elif value == "lower":
        SQL = SQL + """ model = ? AND duct_dim_in = ? AND cfm <= ? ORDER BY cfm DESC LIMIT 1"""        
    elif value == "return_fpm":
        SQL = SQL + """ ? <= cfm AND ((? <= duct_area_sqft AND duct_area_type = 'face') OR (? <= duct_area_sqft AND duct_area_type = 'core'))"""        
    elif value == "return_nc":
        SQL = SQL + """ ? <= cfm AND nc <= ? AND nc <> '' AND type NOT LIKE '%diffuser%' AND velocity_fpm < ?"""
    #endif

    SQL_vars = params #(model, duct_dim_in, cfm,)
    results = do_query(settings, SQL, SQL_vars)                
    
    if len(results) < 1:
        model_specs = 'skip'
    else:
        model_specs = results[0]
        #print("results: " + value
        #print(results
    #endif
    
    return model_specs
#enddef


def output_hardware(models_that_work):
    print("%9s %9s %9s %9s %9s %9s %13s"  % ("Model", "Duct Size", "CFM", "FPM", "Throw", "Spread", "Pressure Loss")
    
    for mtw in models_that_work:
        model, duct_dim_in, cfm, fpm, throw, pressure_loss, spread = mtw    
        cfm    = "{:.1f}".format(cfm)
        fpm    = "{:.1f}".format(fpm)
        throw  = "{:.1f}".format(throw)
        spread = "{:.1f}".format(spread)
        pressure_loss = "{:.3f}".format(pressure_loss)
    

        print("%9s %9s %9s %9s %9s %9s %13s"  % (model, duct_dim_in, cfm, fpm, throw, spread, pressure_loss)
    #endfor
    

#enddef

#------------------------------------------------------------------------------
# Air Entrance Rules (Manual T - Section 10) 
# terminal type = diffuser, register, grille see Section 2
#------------------------------------------------------------------------------
def air_enter_info(settings, project, room):
    if (project.has_option(room,'man_t_location') and project.has_option(room,'man_t_application')):
        junk = 1 #all is well
    else:
        print("Error - man_t_location and/or man_t_application are not defined in config file"
        sys.exit()
    #endif
    project_location    = project.get(room,'man_t_location')
    project_application = project.get(room,'man_t_application') 
    
    #recommeded FPM is 200 for location supply terminals - where does this number come from?
    noise_criteria = get_noise_criteria(settings, project_location, project_application)
    max_nc  = noise_criteria[0]
    max_fpm = noise_criteria[1]
    print("Max noise is (db)           : " + str(max_nc)
    print("Max face/neck velocity (FPM): " + str(max_fpm)
    
    cfm    = float(project.get(room, 'cfm'))
    print("Required CFM for Room: " + str(cfm)
    
    #get/calculate number and location of supply terminals
    num_supply_terminals = 0
    if project.has_option(room, 'num_supply_terminals'):
        num_supply_terminals = int(project.get(room, 'num_supply_terminals'))
        
        #code to check that num_supply_terminals = supply_locationX
        if project.has_option(room, 'supply_location'+str(num_supply_terminals)):
            supply_location = project.get(room,'supply_location'+str(num_supply_terminals))
        else:
            print("Error you need to create the supply_locations for this room"
            sys.exit()
        #endif        
    else:
        num_supply_terminals = max(int(cfm/max_fpm), 1)
        
        print("need to write code to calculate supply_location"
        sys.exit()
    #endif
    print("Number of supply terminals is: " + str(num_supply_terminals)
    
    if num_supply_terminals > 1:
        print("code doesn't handle this right now (line 307)"
        sys.exit()        
    #endif

    #fix the next bit when above get's fixed
    #if supply_location == 'floor':
    #    ttype = '"baseboard","vertical diffuser"'
    #elif supply_location == '
    
#    SQL = 'SELECT model, duct_dim_in, type FROM air_term_mfg_specs WHERE type IN (%s) GROUP BY model, duct_dim_in ORDER BY type' %ttype
    
    SQL = 'SELECT model, duct_dim_in, type FROM air_term_mfg_specs GROUP BY model, duct_dim_in ORDER BY type'
    SQL_vars = ()
    model_info = do_query(settings, SQL, SQL_vars)
    
    
    #GET INFORMATION REGARDING TERMINALS
    for location in range(1, num_supply_terminals+1):        
        supply_info  = project.get(room, 'supply_location'+str(location)).split(',')
        
        #TO DO
        #supply_specs = get_supply_specs(project, room, supply_info, max_nc, max_fpm)
        min_throw  = 8.25 - 2 #supply_specs[0]
        min_spread = (15-4)/2       #supply_specs[1]
        min_spread = (9-2)       #supply_specs[1]
        min_spread = (6-2)       #supply_specs[1]

        min_throw = 5
        


        face_velo  = max_fpm  #supply_specs[2]
        
        #loop over each model, to see how each would work in this room
        models_that_work = []
        for result in model_info:
            model       = result[0]
            duct_dim_in = result[1]
            term_type   = result[2]
            
            #print(model, duct_dim_in, term_type
            
            params = (model, duct_dim_in, cfm,)
            model_specs = get_model_specs(settings, "upper", params)
            if model_specs == 'skip':
                #print("skipping..."
                continue
            #endif
            skip_model = False
            for spec in model_specs:
                if len(str(spec)) < 1:
                    skip_model = True
                    break
                #endif
            #endfor
            if skip_model == True:
                continue
            #endif
            cfm2           = model_specs[0]
            fpm2           = model_specs[1]
            fpm_type2      = model_specs[2]
            throw2         = model_specs[3]
            pressure_loss2 = model_specs[4]
            spread2        = model_specs[5]
            
            model_specs = get_model_specs(settings, "lower", params)
            if model_specs == 'skip':
                #print("skipping..."
                continue
            #endif
            skip_model = False
            for spec in model_specs:
                if len(str(spec)) < 1:
                    skip_model = True
                    break
                #endif
            #endfor
            if skip_model == True:
                continue
            #endif
            cfm1           = model_specs[0]
            fpm1           = model_specs[1]
            fpm_type1      = model_specs[2]
            throw1         = model_specs[3]                    
            pressure_loss1 = model_specs[4]
            spread1        = model_specs[5]

            
            #GOT ALL THE INFO NOW CHECK HARDWARE MEETS REQUIREMENTS
            fpm = interpolate_val(fpm2, fpm1, cfm2, cfm1, cfm)            
            #need max_fpm
            
            #optional - get NC
            #nc = interpolate_val(nc2, nc1, fpm2, fpm1, fpm)            
            #need max_nc
            
            throw = interpolate_val(throw2, throw1, fpm2, fpm1, fpm)            
            #need min_throw
            
            #need to make sure these values are in the database
            spread = interpolate_val(spread2, spread1, fpm2, fpm1, fpm)
            #need min_spread or max_spread...
            
            #maybe report for use in Manual D?
            pressure_loss = interpolate_val(pressure_loss2, pressure_loss1, fpm2, fpm1, fpm)
            
            fpm_OK = False
            if fpm < max_fpm:
                fpm_OK = True                            
            #endif
            
            throw_OK = False
            if throw > min_throw:
                throw_OK = True
            #endif

            spread_OK = False
            if spread > min_spread:
                spread_OK = True
            #endif
            
            if fpm_OK == True and throw_OK == True and spread_OK:
               
                models_that_work.append([model, duct_dim_in, cfm, fpm, throw, pressure_loss, spread])
                
            #endif
            
        #endfor        

        output_hardware(models_that_work)                
    #endfor    
#enddef


#------------------------------------------------------------------------------
# Air Exit Rules (Manual T - Section 11) 
#------------------------------------------------------------------------------
def air_exit_info(settings, project, room):
    if (project.has_option(room,'man_t_location') and project.has_option(room,'man_t_application')):
        junk = 1 #all is well
    else:
        print("Error - man_t_location and/or man_t_application are not defined in config file"
        sys.exit()
    #endif
    
    project_location    = project.get(room,'man_t_location')
    project_application = project.get(room,'man_t_application') 
    
    noise_criteria = get_noise_criteria(settings, project_location, project_application)
    max_nc  = noise_criteria[0]
    max_fpm = noise_criteria[1]
        
    if project.has_option(room,'air_exit_criteria'):
        air_exit_criteria = project.get(room,'air_exit_criteria')
        print("air_exit_criteria is " + air_exit_criteria
    else:
        air_exit_criteria = 'fpm'
        print("air_exit_criteria not supplied, using 'fpm'"
    #endif

    cfm = float(project.get(room, 'cfm'))

    air_exit_path = ''
    air_exit_type = ''    
    if (project.has_option(room, 'air_exit') and project.has_option(room, 'air_exit_type')):
        air_exit_path = project.get(room, 'air_exit')
        air_exit_type = project.get(room, 'air_exit_type')        
    else:        
        print("You need to specifiy the air_exit pathway (return or transfer) and/or the air_exit_type (regular, filter, grille, undercut)"
        sys.exit()
    #endif
   
    if air_exit_path == 'return':                
        print("Return Air"
        
        #------------------------------------------------------------------------------
        #see 11-2 for the following return air grille values
        #why use these vs values in table 10-6?
        #------------------------------------------------------------------------------ 
        if project_location.find('residen') > 0:
            face_velo = 300
            core_velo = 400        
        else:
            face_velo = 400
            core_velo = 500
            print("check the pressure drop - see 11-3"
        #endif
                
        #------------------------------------------------------------------------------
        #see 11-5 for the following filter return air grille values
        #------------------------------------------------------------------------------ 
        if air_exit_type == 'filter':
            face_velo = 200            
            core_velo = 300        
        #endif
        
    elif air_exit_path == 'transfer':
        print("Transfer Air"
        
        #------------------------------------------------------------------------------
        #see 11-4 for the following transfer grille values
        #this is unclear:
        #face_velo may need to be 150 fpm to minimize pressure drop...
        #core_velo = 250 (in that case...?)
        #------------------------------------------------------------------------------         
        face_velo = 200
        core_velo = 300        
        
    else:
        print("ERROR - air_exit not RETURN or TRANSFER - specify in project file"
        sys.exit()        
    #endif
    
    if air_exit_type == 'undercut':
        #undercut: 1 in undercut = 60 CFM 
        undercut_in = cfm / 60
        print("Door undercut = " + str(undercut_in) + " inches"
        if undercut_in > 2:
            print("An undercut of " + str(undercut_in) + " is really too large, you should use a transfer grille instead."
        #endif
    else:
        num_return_terminals = 1
        if project.has_option(room, 'num_return_terminals'):
            num_return_terminals = int(project.get(room, 'num_return_terminals'))
        #endif
    
        cfmpt = cfm / num_return_terminals
        face_area = float("{:1.3f}".format(cfmpt / face_velo))
        core_area = float("{:1.3f}".format(cfmpt / core_velo))
        print("Face area for " + str(num_return_terminals) + " " + air_exit_path + " " + air_exit_type + " = " + str(face_area) + " sq. ft."
        print("Core area for " + str(num_return_terminals) + " " + air_exit_path + " " + air_exit_type + " = " + str(core_area) + " sq. ft."
        print("CFM per terminal is " + str(cfmpt)
        
        SQL = """SELECT model, duct_dim_in FROM air_term_mfg_specs GROUP BY model, duct_dim_in"""
        SQL_vars = ()
        model_info = do_query(settings, SQL, SQL_vars)
        
        #GET INFORMATION REGARDING TERMINALS
        #loop over each model, to see how each would work in this room
        models_that_work = []
        for result in model_info:
            model       = result[0]
            duct_dim_in = result[1]
                
            #print(model, duct_dim_in
         
            if air_exit_criteria == 'nc':
                print("Search for returns that can handle " + str(cfmpt) + " CFM with a NC <= " + str(max_nc)
                print("Smaller velocity and pressure values are better"
            
                params = (cfmpt,max_nc,max_fpm,)
                model_specs = get_model_specs(settings, "return_nc", params)
                if model_specs == 'skip':
                    #print("skipping..."
                    continue
                #endif            
            else: #using FPM                        
                params = ( cfmpt, face_area, core_area,)
                model_specs = get_model_specs(settings, "return_fpm", params)
                if model_specs == 'skip':
                    #print("skipping..."
                    continue
                #endif
            #endif
            
            print("FIX-ME - this should probably be same as earlier"            
            #print(model_specs
            cfm           = model_specs[0]
            fpm           = model_specs[1]
            fpm_type      = model_specs[2]
            throw         = model_specs[3]                    
            pressure_loss = model_specs[4]
            spread        = model_specs[5]
            
            #do some more filtering here??
            models_that_work.append([model, duct_dim_in, cfm, fpm, throw, pressure_loss, spread])
                
            #endif
            
        #endfor        

        output_hardware(models_that_work)



    #endif
    
#enddef

#------------------------------------------------------------------------------
# MAIN CODE HERE
# need to check that all rooms have either transfer or return air_exit
# need to check that all zones have return air_exit somewhere
#...
#------------------------------------------------------------------------------
def air_distribution(project):
    project_name = project.get('Location', 'project_name')    
    print("Doing manual T for " + project_name
    
    #read the system settings file (maybe should be in own module - along w/ get_database name)
    settings = configparser.Safeconfigparser()
    settings_file = os.path.abspath('system_settings.txt')
    settings.read(settings_file)
    
    num_zones = int(project.get('Zones', 'num_zones'))
    for zone in range (1, num_zones+1):        
        zone_section = 'Zone ' + str(zone)
        print(zone_section
        list_rooms = project.get(zone_section, 'list_rooms').split(',')        
        for room in list_rooms:
            room_section = 'Room ' + str(room)
            print(room_section
            print("-------------------------------------------"
            print("Calculating Supply information - Section 10"
            air_enter_info(settings, project, room_section)
            print("-------------------------------------------"
            print("Calculating Return information - Section 11"
            air_exit_info(settings, project, room_section)
            
        #endfor
    #endfor        
#enddef

if __name__ == '__main__':
    print("Doing air distribution (Manual T) - standalone"
    
    #maybe should check the data as part of the startup procedure...
        
    project = configparser.Safeconfigparser()
    
    project_file = os.path.abspath('projects/man_t_ex10-9.txt')
    #project_file = os.path.abspath('projects/man_t_ex10-11.txt')
    #project_file = os.path.abspath('projects/man_t_ex10-12.txt')
    #project_file = os.path.abspath('projects/man_t_ex10-14.txt')
    
    #project_file = os.path.abspath('projects/man_t_ex11-6.txt')
    #project_file = os.path.abspath('projects/man_t_ex11-7.txt')
    #project_file = os.path.abspath('projects/man_t_ex11-8.txt')
    
    project.read(project_file)
        
    air_distribution(project)
    
#endif
