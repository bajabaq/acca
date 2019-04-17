#------------------------------------------------------------------
# Worksheet A - Indoor and outdoor design conditions
#------------------------------------------------------------------
import sys

import hvac_database
import hvac_math

def output_worksheet_a(results):
    project_name      = results['project']
    city              = results['city']
    state             = results['state']
    elevation         = results['elevation']
    latitude          = results['latitude']
    indoor_heating_db = results['indoor_heating_db']
    indoor_heating_rh = results['indoor_heating_rh']
    indoor_cooling_db = results['indoor_cooling_db']
    indoor_cooling_rh = results['indoor_cooling_rh']
    outdoor_99per_db  = results['outdoor_99per_db']
    outdoor_1per_db   = results['outdoor_1per_db']
    grains_diff       = results['grains_diff']
    daily_range       = results['daily_range']
    htd               = results['htd']
    ctd               = results['ctd']
    acf               = results['acf']
    
    if daily_range == 'm':
        daily_range = 'medium'
    elif daily_range == 'l':
        daily_range = 'large'
    #endif
    msg = ""
    msg = msg +  60 * "=" + "\n"
    msg = msg +  "Worksheet A: Indoor and Outdoor Design Conditions" + "\n"
    msg = msg +  60 * "-" + "\n"
    msg = msg +  "Project             : %10s" % (project_name) + "\n"
    msg = msg +  "City, State         : %15s, %2s" % ( city, state) + "\n"
    msg = msg +  "Table 1A Latitude   : %3s" % (latitude) + "\n"
    msg = msg +  "Table 1A Elevation  : %3s" % (elevation) + "\n"
    msg = msg +  "Indoor Conditions" + "\n"
    msg = msg +  "    Heating DryBulb : %2s" % (indoor_heating_db) + "\n"
    msg = msg +  "    Winter (Heating) humidifcation : ???? - FIX ME" + "\n"
    #msg = msg +  "Indoor Conditions, Heating Re:  RH = " + str(indoor_conditions_heating_rh)
    msg = msg +  "    Cooling DryBulb : %2s" % (indoor_cooling_db) + "\n"
    msg = msg +  "    Cooling RH%%     : %2s" % (indoor_cooling_rh) + "\n"
    msg = msg +  "Outdoor Design Conditions" + "\n"
    msg = msg +  "    99%% DryBulb     : %2s" % (outdoor_99per_db) + "\n"
    msg = msg +  "     1%% DryBulb     : %2s" % (outdoor_1per_db) + "\n"
    msg = msg +  "   Grains Difference: %2s" % (grains_diff) + "\n"
    msg = msg +  "         Daily Range: %2s" % (daily_range) + "\n"
    msg = msg +  "Heating temperature difference (HTD)  : %2s" % (htd) + "\n"
    msg = msg +  "Cooling temperature difference (CTD)  : %2s" % (ctd) + "\n"
    msg = msg +  "Table 10A ACF                         : %.2f" % (acf) + "\n"
    #msg = msg +  "Air Density                        = " + str(ad)
    msg = msg +  60 * "=" + "\n"
    
    print(msg)
    
#enddef


#------------------------------------------------------------------------------
#get air correction factor and air_density with respect to altitude and elevation
#need to figure out what happens when outside of range (or what to do in that case)
#------------------------------------------------------------------------------
def get_altitude_info(settings, elevation):
    
    [math_type2, (alt2,acf2,air_den2)] = get_altitude_info_aux(settings, 'upper', elevation)    
    [math_type1, (alt1,acf1,air_den1)] = get_altitude_info_aux(settings, 'lower', elevation)
    
    if (math_type2 == 'interpolate' and math_type1 == 'interpolate'):
        acf     = hvac_math.interpolate_val(acf2, acf1, alt2, alt1, elevation)                
        air_den = hvac_math.interpolate_val(air_den2, air_den1, alt2, alt1, elevation) 
    elif (math_type2 == 'extrapolate'):
        print("extrapolating forward...")
        alt2     = alt1
        acf2     = acf1
        air_den2 = air_den1
        [_x, (alt1,acf1,air_den1)] = get_altitude_info_aux(settings, 'lower', (alt1-1))
        acf     = hvac_math.extrapolate_val(acf2, acf1, alt2, alt1, elevation)                
        air_den = hvac_math.extrapolate_val(air_den2, air_den1, alt2, alt1, elevation) 
    elif (math_type1 == 'extrapolate'):
        print("extrapolating backward...")
        alt1     = alt2
        acf1     = acf2
        air_den1 = air_den2
        [_x, (alt2,acf2,air_den2)] = get_altitude_info_aux(settings, 'upper', (alt2+1))
        acf     = hvac_math.extrapolate_val(acf2, acf1, alt2, alt1, elevation)                
        air_den = hvac_math.extrapolate_val(air_den2, air_den1, alt2, alt1, elevation) 
    #endif
    #acf = 2sig figs, air_den = 3 sig figs in data table - but leaving these for now
    
    acf     = float("{0:.5f}".format(acf))
    air_den = float("{0:.6f}".format(air_den))
    
    return acf, air_den
#enddef

def get_altitude_info_aux(settings, value, elevation):
    SQL = ''
    extrapolate_dir = ''
    if value == "lower":
        SQL = """SELECT altitude, acf, lbpercf FROM altitude_info WHERE altitude <= ? ORDER BY altitude DESC LIMIT 1"""    
        extrapolate_dir  = 'backward'
        elevation_adjust = -1000
    elif value == "upper":
        SQL = """SELECT altitude, acf, lbpercf FROM altitude_info WHERE ? <= altitude ORDER BY altitude ASC LIMIT 1"""    
        extrapolate_dir = 'forward'
        elevation_adjust = 1000
    #endif
    SQL_vars = (elevation,)
    results  = hvac_database.do_query(settings, SQL, SQL_vars)                

    altitude_info = []
    if len(results) < 1:
        msg = "WARNING - have to extrapolate " + extrapolate_dir + " to determine values at elevation: " + str(elevation)
        print(msg)
        altitude_info = ['extrapolate',(0,0,0)]
    else:
        res = results[0]
        for v in results[0]:
            if v == '':   #meaning value not in database (will only work if missing y-val: acf or air_den)
                adj_altitude_info = get_altitude_info_aux(settings, value, elevation + elevation_adjust)
                res = adj_altitude_info[1]
            #endif
        #endfor
    
        altitude_info = ['interpolate',res]

    #endif
    
    return altitude_info
#enddef


def get_humidity_info(coil_climate, design_grains_55per_rh, design_grains_50per_rh, design_grains_45per_rh):
    if coil_climate == 'wet':
        indoor_cooling_rh = 50  #preferred for wet-coil climate        
        grains_diff = design_grains_50per_rh
    elif coil_climate == 'dry':
        indoor_cooling_rh = 45  #for dry-coil climate (2B southwest)
        grains_diff = design_grains_45per_rh
    elif coil_climate == 'super_wet':
        indoor_cooling_rh = 55  #acceptible for really wet-coil climates (1A - miami)
        grains_diff = design_grains_55per_rh
    #endif
    return indoor_cooling_rh, grains_diff
#enddef


#------------------------------------------------------------------------------
# Get the coil climate - see pg 454 - wet, dry, super_wet
# insignificant latent-load, coil climate = dry (45% indoor RH)
# has a latent-load,         coil climate = wet (50% indoor RH)        
# has a large latent-load,   coil climate = super_wet (55% indoor RH is OK)
# wet       = normal
# dry       = type B - Maybe... This is based on the amount of precipitation and the annual mean temperature. 
#                      The calculation is 0.44 x (TF - 19.5), where TF is the annual mean temperature in degrees Fahrenheit. 
#                      If the annual precipitation is less than the number you get, it's a dry climate and the zone number has a B after it.
# super_wet = 1A - Miami  https://energycode.pnl.gov/EnergyCodeReqs/index.jsp?state=Florida
#
# zone A = not zone C 
#
# Zone C is the Goldilocks climate. It is not too hot in the summer (Warmest month mean temperature < 72 F), 
#                                                            not too cold or too warm in winter (between 27 and 65 F), 
#                                                            has at least four months with mean temperatures above 50 F, 
#                                                            and has its dry season in the summer. 
#                       Ex: Santa Barbara (3C), Portland (4C), and Seattle (4C). http://www.greenbuildingadvisor.com/blogs/dept/building-science/all-about-climate-zones)
#
#
#algorithim is: find zone (Is C, B, or A)
#then find number (1-8 - see http://www.greenbuildingadvisor.com/blogs/dept/building-science/all-about-climate-zones table)
#
#see coil_climate_calc.ods
#
#------------------------------------------------------------------------------
def get_coil_climate(state, city):
    #maybe need to do a calculation, but for now a lookup is good
    if state == 'texas' and city == 'houston ap':
        coil_climate = 'wet'
    elif state == 'indiana' and city == 'lafayette':
        coil_climate = 'wet'
    elif state == 'georgia' and city == 'augusta ap':
        coil_climate = 'wet'
    elif state == 'florida' and city == 'miami':
        coil_climate = 'super_wet'
    elif state == 'arizona' and city == 'phoenix':
        coil_climate = 'dry'    
    else:
        print("Error - get_coil_climate needs to expand lookup or do calculation")
        sys.exit()
    #endif
    return coil_climate
#enddef


#------------------------------------------------------------------------------
# indoor and outdoor design conditions
#------------------------------------------------------------------------------
def worksheet_a(settings, project):
    project_name = project.get('Location', 'project_name')
    state        = project.get('Location', 'design_state')
    city         = project.get('Location', 'design_city')
    
    SQL = """SELECT elevation, latitude, heating_99per_db, cooling_1per_db, concident_wb, \
                    design_grains_55per_rh, design_grains_50per_rh, design_grains_45per_rh, \
                    daily_range \
             FROM outdoor_design_cond WHERE state = ? AND city = ?""" 
    SQL_vars = (state, city,)
    results  = hvac_database.do_query(settings, SQL, SQL_vars) 
    
    outdoor_design_cond    = results[0]
    elevation              = outdoor_design_cond[0]
    latitude               = outdoor_design_cond[1]
    outdoor_99per_db       = outdoor_design_cond[2]
    outdoor_1per_db        = outdoor_design_cond[3]
    concident_wb           = outdoor_design_cond[4]
    design_grains_55per_rh = outdoor_design_cond[5]
    design_grains_50per_rh = outdoor_design_cond[6]
    design_grains_45per_rh = outdoor_design_cond[7]
    daily_range            = outdoor_design_cond[8]
    
    #TODO
    #use project address to lookup and see if the defaults are superceded by local code    
    
    #Indoor Design Parameters for Cooling (maybe get from settings file) - use these unless superceded by local code
    #see fig3-1 p15
    indoor_cooling_db = 75
    
    #use design address to check to see/calculate if in wet-coil or dry-coil climate    
    #maybe move this above to get only 1 design_grains...
    coil_climate = get_coil_climate(state, city)
    indoor_cooling_rh, grains_diff = get_humidity_info(coil_climate, design_grains_55per_rh, design_grains_50per_rh, design_grains_45per_rh)

    #Indoor Design Parameters for Heating (maybe get from settings file) - use these unless superceded by local code
    #winter humidification is optional and the humidification level shall not cause visible or concealed condensation
    #see fig3-1 p15
    indoor_heating_db = 70
    indoor_heating_rh = ''
    
    #heating and cooling temperature difference
    htd = indoor_heating_db - outdoor_99per_db
    ctd = outdoor_1per_db   - indoor_cooling_db
    
    #altitude correction
    acf, air_den = get_altitude_info(settings, elevation)
    
    results = {'project'          :project_name,
               'city'             :city,
               'state'            :state,
               'elevation'        :elevation,        
               'latitude'         :latitude,         
               'indoor_heating_db':indoor_heating_db,
               'indoor_heating_rh':indoor_heating_rh,
               'indoor_cooling_db':indoor_cooling_db,
               'indoor_cooling_rh':indoor_cooling_rh,
               'outdoor_99per_db' :outdoor_99per_db,
               'outdoor_1per_db'  :outdoor_1per_db,  
               'grains_diff'      :grains_diff,      
               'daily_range'      :daily_range,      
               'htd'              :htd,              
               'ctd'              :ctd,
               'acf'              :acf,
               'air_den'          :air_den}

    output_worksheet_a(results)
    
    return results
#endfunc
