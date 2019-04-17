

#------------------------------------------------------------------------------
#   Worksheet G: 
#------------------------------------------------------------------------------

import sys
from hvac_database import get_db_filename, do_query
from hvac_math import round_ctd, interpolate_val
import load_calc_wksht_aux



def get_default_surface_areas(settings, construction_number,surface_area,floor_area):

    params = (construction_number, floor_area,)
    SQL = ''
    if surface_area == 'supply' :
        SQL = """SELECT floor_area, supply FROM duct_load_default_surface_area WHERE construction_number = ? AND floor_area <= ? ORDER BY floor_area DESC LIMIT 1"""
    else:
        SQL = """SELECT floor_area, return FROM duct_load_default_surface_area WHERE construction_number = ? AND floor_area <= ? ORDER BY floor_area DESC LIMIT 1"""
    #endif
    SQL_vars = params
    lower_results  = do_query(settings, SQL, SQL_vars)

    lower_info = []
    if len(lower_results) < 1:
        print("ERROR")
        lower_info = 'skip'
        sys.exit()
    else:
        lower_info = lower_results[0]
    #endif

    if surface_area == 'supply' :
        SQL = """SELECT floor_area, supply FROM duct_load_default_surface_area WHERE construction_number = ? AND floor_area >= ? ORDER BY floor_area ASC LIMIT 1"""
    else:
        SQL = """SELECT floor_area, return FROM duct_load_default_surface_area WHERE construction_number = ? AND floor_area >= ? ORDER BY floor_area ASC LIMIT 1"""
    #endif
    upper_results  = do_query(settings, SQL, SQL_vars)                
    upper_info = []
    if len(upper_results) < 1:
        print("ERROR")
        upper_info = 'skip'
        sys.exit()
    else:
        upper_info = upper_results[0]
    #endif
    
    f_lower   = lower_info[0]
    f_upper   = upper_info[0]
    sa_lower  = lower_info[1]
    sa_upper  = upper_info[1]
    sa_interp = interpolate_val(sa_lower, sa_upper, f_lower, f_upper, floor_area )

    return sa_interp
#enddef


def get_query_aux(results):
    info = []
    if len(results) < 1:
        print( "ERROR" )
        info = 'skip'
        sys.exit()
    else:
        info = results[0]
        #print "results: " + value
        #print results
    #endif
    res = info[0]
    return res
#enddef


def get_leakage_factor(settings, ctype, results):
    leakage = str(results['leakage_supply']) + '/' + str(results['leakage_return'])

    params = (results['construction_number'],leakage,results['rval'],)
    SQL = ''
    #lower(upper)area_lower(upper)temp
    if ctype == "heat_loss":
        SQL = """SELECT heat_loss_correction FROM duct_load_leakage WHERE construction_number = ? AND leakage = ? AND rval = ? """
    elif ctype == "sensible":
        SQL = """SELECT sensible_correction FROM duct_load_leakage WHERE construction_number = ? AND leakage = ? AND rval = ? """
    elif ctype == "latent":
        SQL = """SELECT latent_correction FROM duct_load_leakage WHERE construction_number = ? AND leakage = ? AND rval = ? """
    #endif
    SQL_vars = params
    results  = do_query(settings, SQL, SQL_vars)                
    
    #print results
    val = get_query_aux(results)

    return val
#enddef

def get_rval_correction(settings, ctype, results):
    params = (results['construction_number'],results['rval'],)
    SQL = ''
    #lower(upper)area_lower(upper)temp
    if ctype == "bhlf":
        SQL = """SELECT bhlf_correction FROM duct_load_rval_correction WHERE construction_number = ? AND rval = ? """
    elif ctype == "bsgf":
        SQL = """SELECT bsgf_correction FROM duct_load_rval_correction WHERE construction_number = ? AND rval = ? """
    #endif
    SQL_vars = params
    results  = do_query(settings, SQL, SQL_vars)                
    
    #print results
    rval = get_query_aux(results)

    return rval
#enddef

def get_surface_area_factor(settings, construction_number, leakage_type, leakage):
    params = (construction_number,leakage_type,leakage,)
    SQL = """SELECT k FROM duct_load_surface_area_factors WHERE construction_number = ? AND leakage_type = ? AND leakage = ? """
    SQL_vars = params
    results  = do_query(settings, SQL, SQL_vars)                
    
    #print results
    k = get_query_aux(results)

    return k
#enddef


#------------------------------------------------------------------------------
#need to figure out what happens when outside of range (or what to do in that case)
#------------------------------------------------------------------------------
def get_heat_loss_factor(settings, value, results):
    params = (results['construction_number'],results['outdoor_99per_db'], results['floor_area_heating'],)
    SQL = ''
    #lower(upper)area_lower(upper)temp
    if value == "la_lt":
        SQL = """SELECT bhlf, floor_area, oat FROM duct_load_bhlf WHERE construction_number = ? AND oat <= ? AND floor_area <= ? ORDER BY oat DESC , floor_area DESC LIMIT 1"""    
    elif value == "ua_lt":
        SQL = """SELECT bhlf, floor_area, oat FROM duct_load_bhlf WHERE construction_number = ? AND oat <= ? AND ? <= floor_area  ORDER BY oat DESC, floor_area ASC LIMIT 1"""  
    elif value == "la_ut":
        SQL = """SELECT bhlf, floor_area, oat FROM duct_load_bhlf WHERE construction_number = ? AND oat >= ? AND floor_area <= ? ORDER BY oat DESC, floor_area ASC LIMIT 1"""  
    elif value == "ua_ut":
        SQL = """SELECT bhlf, floor_area, oat FROM duct_load_bhlf WHERE construction_number = ? AND oat >= ? AND ? <= floor_area  ORDER BY oat DESC, floor_area ASC LIMIT 1"""  
    #endif
    SQL_vars = params
    results  = do_query(settings, SQL, SQL_vars)                
    
    #print results

    hlf_info = []
    if len(results) < 1:
        print( "ERROR"        )
        hlf_info = 'skip'
    else:
        hlf_info = results[0]
        #print "results: " + value
        #print results
    #endif
    
    return hlf_info
#enddef

def get_sensible_gain_factor(settings, value, results):
    params = (results['construction_number'],results['outdoor_1per_db'], results['floor_area_cooling'],)
    SQL = ''
    #lower(upper)area_lower(upper)temp
    if value == "la_lt":
        SQL = """SELECT bsgf, floor_area, oat FROM duct_load_bsgf WHERE construction_number = ? AND oat <= ? AND floor_area <= ? ORDER BY oat DESC , floor_area DESC LIMIT 1"""    
    elif value == "ua_lt":
        SQL = """SELECT bsgf, floor_area, oat FROM duct_load_bsgf WHERE construction_number = ? AND oat <= ? AND ? <= floor_area  ORDER BY oat DESC, floor_area ASC LIMIT 1"""  
    elif value == "la_ut":
        SQL = """SELECT bsgf, floor_area, oat FROM duct_load_bsgf WHERE construction_number = ? AND oat >= ? AND floor_area <= ? ORDER BY oat DESC, floor_area ASC LIMIT 1"""  
    elif value == "ua_ut":
        SQL = """SELECT bsgf, floor_area, oat FROM duct_load_bsgf WHERE construction_number = ? AND oat >= ? AND ? <= floor_area  ORDER BY oat DESC, floor_area ASC LIMIT 1"""  
    #endif
    SQL_vars = params
    results  = do_query(settings, SQL, SQL_vars)                
    
    #print results

    info = []
    if len(results) < 1:
        print ("ERROR"        )
        info = 'skip'
    else:
        info = results[0]
        #print "results: " + value
        #print results
    #endif
    
    return info
#enddef

def get_latent_gain_factor(settings, value, results):
    params = (results['construction_number'],results['grains_diff'], results['floor_area_cooling'],)
    SQL = ''
    #lower(upper)area_lower(upper)temp
    if value == "la_lt":
        SQL = """SELECT blg, floor_area, grains FROM duct_load_blg WHERE construction_number = ? AND grains <= ? AND floor_area <= ? ORDER BY grains DESC , floor_area DESC LIMIT 1"""    
    elif value == "ua_lt":
        SQL = """SELECT blg, floor_area, grains FROM duct_load_blg WHERE construction_number = ? AND grains <= ? AND ? <= floor_area  ORDER BY grains DESC, floor_area ASC LIMIT 1"""  
    elif value == "la_ut":
        SQL = """SELECT blg, floor_area, grains FROM duct_load_blg WHERE construction_number = ? AND grains >= ? AND floor_area <= ? ORDER BY grains DESC, floor_area ASC LIMIT 1"""  
    elif value == "ua_ut":
        SQL = """SELECT blg, floor_area, grains FROM duct_load_blg WHERE construction_number = ? AND grains >= ? AND ? <= floor_area  ORDER BY grains DESC, floor_area ASC LIMIT 1"""  
    #endif
    SQL_vars = params
    results  = do_query(settings, SQL, SQL_vars)                
    
    #print results

    info = []
    if len(results) < 1:
        print("ERROR"        )
        info = 'skip'
    else:
        info = results[0]
        #print "results: " + value
        #print results
    #endif
    
    return info
#enddef


def get_factor_top(settings, factor, results):
    ua_lt_results = []
    la_lt_results = []
    ua_ut_results = []
    la_ut_results = []
    area = 0
    temp_or_grains = 0
    
    #print(factor)
    
    if factor == 'heat_loss':
        ua_lt_results = get_heat_loss_factor(settings, 'ua_lt', results)
        la_lt_results = get_heat_loss_factor(settings, 'la_lt', results)

        ua_ut_results = get_heat_loss_factor(settings, 'ua_ut', results)
        la_ut_results = get_heat_loss_factor(settings, 'la_ut', results)
        area = results['floor_area_heating']
        temp_or_grains = results['outdoor_99per_db']
    elif factor == 'sensible_gain':
        ua_lt_results = get_sensible_gain_factor(settings, 'ua_lt', results)
        la_lt_results = get_sensible_gain_factor(settings, 'la_lt', results)

        ua_ut_results = get_sensible_gain_factor(settings, 'ua_ut', results)
        la_ut_results = get_sensible_gain_factor(settings, 'la_ut', results)
        area = results['floor_area_cooling']
        temp_or_grains = results['outdoor_1per_db']
    elif factor == 'latent_gain':
        ua_lt_results = get_latent_gain_factor(settings, 'ua_lt', results)
        la_lt_results = get_latent_gain_factor(settings, 'la_lt', results)

        ua_ut_results = get_latent_gain_factor(settings, 'ua_ut', results)
        la_ut_results = get_latent_gain_factor(settings, 'la_ut', results)
        area = results['floor_area_cooling']
        temp_or_grains = results['grains_diff']
    else:
        print( "Error - factor ( "+ factor + " ) not found")
        sys.exit()
    #endif
    
    f_ualt    = ua_lt_results[0]
    f_lalt    = la_lt_results[0]
    area_ualt = ua_lt_results[1]
    area_lalt = la_lt_results[1]
    temp_lt   = la_lt_results[2]
    f_lt      = interpolate_val(f_ualt, f_lalt, area_ualt, area_lalt, area)
    
    f_uaut    = ua_ut_results[0]
    f_laut    = la_ut_results[0]
    area_uaut = ua_ut_results[1]
    area_laut = la_ut_results[1]
    temp_ut   = la_ut_results[2]
    f_ut      = interpolate_val(f_uaut, f_laut, area_uaut, area_laut, area)

    factor    = interpolate_val(f_ut, f_lt, temp_ut, temp_lt, temp_or_grains)
#    print factor
    
    return factor
#enddef


def get_surface_area(surface_area, num_pipes, part_pipe_section, duct_section, project):
    pi = 3.1415927
    for pipe in range (1, num_pipes + 1):
        pipe_section = duct_section + part_pipe_section + str(pipe)
        print(8*' ' + pipe_section)
        pipe_diameter = float(project.get(pipe_section, 'diameter'))
        pipe_length   = float(project.get(pipe_section, 'length'))
        surface_area = surface_area + pipe_diameter * pi * pipe_length
    #endfor
    return surface_area
#enddef

def output_worksheet_g(results):
    msg = ""
    msg = msg +  60 * "=" + "\n"
    msg = msg +  "Worksheet G: Duct Runs in Unconditioned Space" + "\n"
    msg = msg +  60 * "-" + "\n"
    msg = msg +  "Duct Load Table                  : " + results['construction_number'] + "\n"
    msg = msg +  "Floor Area (Heating) sqft        : " + str(results['floor_area_heating']) + "\n"
    msg = msg +  "Floor Area (Cooling) sqft        : " + str(results['floor_area_cooling']) + "\n"
    msg = msg +  "99% dry bulb                     : " + str(results['outdoor_99per_db']) + "\n"
    msg = msg +  " 1% dry bulb                     : " + str(results['outdoor_1per_db']) + "\n"
    msg = msg +  "Grains Difference                : " + str(results['grains_diff']) + "\n"
    msg = msg +  "" + "\n"
    msg = msg +  "Existing / Proposed Construction " + "\n"
    msg = msg +  "R-Value                          : " + str(results['rval']) + "\n"
    msg = msg +  "Leakage                          : " + str(results['leakage_supply']) + "/" + str(results['leakage_return']) + "\n"
    msg = msg +  "" + "\n"
    msg = msg +  "Base-case factors from table (interpolated, but uncorrected)" + "\n"
    msg = msg +  " 1) Heat loss factor             : " + str(results['heat_loss_factor']) + "\n"
    msg = msg +  " 2) Sensible gain factor         : " + str(results['sensible_gain_factor']) + "\n"
    msg = msg +  " 3) Latent gain factor           : " + str(results['latent_gain_factor']) + "\n"
    msg = msg +  "" + "\n"
    msg = msg +  "R-Value Correction (WIF)" + "\n"
    msg = msg +  " 4) For heat loss                : " + str(results['rval_bhlf_correction']) + "\n"
    msg = msg +  " 5) For sensible gain            : " + str(results['rval_bsgf_correction']) + "\n"
    msg = msg +  " 6) Adjusted heat loss factor    : " + str(results['adj_hlf']) + "\n"
    msg = msg +  " 7) Adusted sensible gain factor : " + str(results['adj_sgf']) + "\n"
    msg = msg +  "" + "\n"
    msg = msg +  "Leakage Rate Correction (LCF)" + "\n"
    msg = msg +  " 8) For heat loss                     : " + str(results['lcf_heat_loss']) + "\n"
    msg = msg +  " 9) For sensible gain                 : " + str(results['lcf_sensible_gain']) + "\n"
    msg = msg +  "10) For latent gain                   : " + str(results['lcf_latent_gain']) + "\n"
    msg = msg +  "11) Adjusted heat loss factor         : " + str(results['adj_lcf_hlf']) + "\n"
    msg = msg +  "12) Adjusted sensible gain factor     : " + str(results['adj_lcf_sgf']) + "\n"
    msg = msg +  "13) Adjusted latent gain              : " + str(results['adj_lcf_lgf']) + "\n"
    msg = msg +  "" + "\n"
    msg = msg +  "Surface Area Adjustment (default for new construction = no adjustment = 1.0)" + "\n"
    msg = msg +  "14) Installed supply area             : " + str(results['supply_area']) + "\n"
    msg = msg +  "15) Default supply area               : " + str(results['default_sa']) + "\n"
    msg = msg +  "16) Rs = Installed / Default area     : " + str(results['rs']) + "\n"
    msg = msg +  "17) Installed return area             : " + str(results['return_area']) + "\n"
    msg = msg +  "18) Default return area               : " + str(results['default_ra']) + "\n"
    msg = msg +  "19) Rr = Installed / Default area     : " + str(results['rr']) + "\n"
    msg = msg +  "20a)                               Ks : " + str(results['ks']) + "\n"
    msg = msg +  "20b)                               Kr : " + str(results['kr']) + "\n"
    msg = msg +  "21) SAA (heating and sensible cooling): " + str(results['saa']) + "\n"
    msg = msg +  "22) LGA (latent cooling)              : " + str(results['rr']) + "\n"  
    msg = msg +  "" + "\n"
    msg = msg +  "Heat Loss and Heat Gain factors and Latent Gain" + "\n"
    msg = msg +  "23) Net heat loss factor              : " + str(results['nhlf']) + "\n"
    msg = msg +  "24) Net sensible gain factor          : " + str(results['nsgf']) + "\n"
    msg = msg +  "25) Net latent gain                   : " + str(results['nlg']) + "\n"
    
    msg = msg +  60 * "=" + "\n"
    
    print(msg)
#enddef

def get_rest_results(settings, results, project):
    heat_loss_factor = get_factor_top(settings, 'heat_loss', results)
    results['heat_loss_factor'] = heat_loss_factor
    
    sensible_gain_factor = get_factor_top(settings, 'sensible_gain', results)
    results['sensible_gain_factor'] = sensible_gain_factor
    
    latent_gain_factor = get_factor_top(settings, 'latent_gain', results)
    results['latent_gain_factor'] = latent_gain_factor

    rval_bhlf_correction = get_rval_correction(settings, 'bhlf', results)
    rval_bsgf_correction = get_rval_correction(settings, 'bsgf', results)
    results['rval_bhlf_correction'] = rval_bhlf_correction
    results['rval_bsgf_correction'] = rval_bsgf_correction
    
    adj_hlf = heat_loss_factor * rval_bhlf_correction
    adj_sgf = sensible_gain_factor * rval_bsgf_correction
    results['adj_hlf'] = adj_hlf
    results['adj_sgf'] = adj_sgf        
    
    lcf_heat_loss     = get_leakage_factor(settings, 'heat_loss', results)
    lcf_sensible_gain = get_leakage_factor(settings, 'sensible' , results)
    lcf_latent_gain   = get_leakage_factor(settings, 'latent'   , results)
    results['lcf_heat_loss']     = lcf_heat_loss
    results['lcf_sensible_gain'] = lcf_sensible_gain
    results['lcf_latent_gain']   = lcf_latent_gain
    
    
    results['adj_lcf_hlf'] = adj_hlf * lcf_heat_loss
    results['adj_lcf_sgf'] = adj_sgf * lcf_sensible_gain
    results['adj_lcf_lgf'] = latent_gain_factor * lcf_latent_gain       

    duct_section = results['duct_section']
    num_supply_trunks   = int(project.get(duct_section, 'num_supply_trunks'))
    num_supply_branches = int(project.get(duct_section, 'num_supply_branches'))
    num_return_trunks   = int(project.get(duct_section, 'num_supply_trunks'))

    supply_area = 0
    supply_area = get_surface_area(supply_area, num_supply_trunks  , ' Supply Trunk ' , duct_section, project)
    supply_area = get_surface_area(supply_area, num_supply_branches, ' Supply Branch ', duct_section, project)

    return_area = 0
    return_area = get_surface_area(return_area, num_return_trunks, ' Return Trunk ', duct_section, project)

    results['supply_area'] = supply_area
    results['return_area'] = return_area
        
    default_sa = get_default_surface_areas(settings, results['construction_number'],'supply',results['floor_area_cooling'])
    default_ra = get_default_surface_areas(settings, results['construction_number'],'return',results['floor_area_cooling'])
    results['default_sa'] = default_sa
    results['default_ra'] = default_ra
    
    results['rs']   = supply_area / default_sa
    results['rr']   = return_area / default_ra
    
    results['ks']   = get_surface_area_factor(settings, results['construction_number'], 'supply', results['leakage_supply'])
    results['kr']   = get_surface_area_factor(settings, results['construction_number'], 'return', results['leakage_return'])
    results['saa']  = results['ks'] * results['rs'] + results['kr'] * results['rr'] 
    
    results['nhlf'] = results['adj_lcf_hlf'] * results['saa']
    results['nsgf'] = results['adj_lcf_sgf'] * results['saa']
    results['nlg']  = results['adj_lcf_lgf'] * results['rr']

    return results
#enddef



#------------------------------------------------------------------------------
#   Worksheet G: Duct Runs in Unconditioned Space
#------------------------------------------------------------------------------
def worksheet_g(settings, project, a_results):
    results = {
        'outdoor_99per_db'   : a_results['outdoor_99per_db'],
        'outdoor_1per_db'    : a_results['outdoor_1per_db'],
        'grains_diff'        : a_results['grains_diff']
    }
    
    num_zones = int(project.get('Zones', 'num_zones'))
    for zone in range (1, num_zones+1):        
        zone_section = 'Zone ' + str(zone)
        print(zone_section)

        floor_area_heating = load_calc_wksht_aux.get_conditioned_floor_area(project, zone_section, 'heated')
        results['floor_area_heating'] = floor_area_heating
        floor_area_cooling = load_calc_wksht_aux.get_conditioned_floor_area(project,zone_section,'cooled')
        results['floor_area_cooling'] = floor_area_cooling
        
        if floor_area_heating != floor_area_cooling:
            print("WARNING!!! heating and cooling floor areas differ - assumptions below may be wrong!!!!")
            sys.exit()
        #endif
        
        duct_section = zone_section + ' Duct 1' #only 1 duct_section per zone (I think)
        results['duct_section'] = duct_section
            
        construction_number = project.get(duct_section, 'construction_number')
        results['construction_number'] = construction_number
        
        rval = project.get(duct_section, 'r-val')
        results['rval'] = rval

        leakage_supply = project.get(duct_section, 'leakage_supply')
        results['leakage_supply'] = leakage_supply
        leakage_return = project.get(duct_section, 'leakage_return')
        results['leakage_return'] = leakage_return

        results = get_rest_results(settings, results, project)
        
        output_worksheet_g(results)

        #maybe need to test all 3 improved factors
        if project.has_option(duct_section, 'improved_r-val'):
            print("\nDoing improved construction\n")
            iresults = results.copy()
            
            rval = project.get(duct_section, 'improved_r-val')
            iresults['rval'] = rval
            
            leakage_supply = project.get(duct_section, 'improved_leakage_supply')
            iresults['leakage_supply'] = leakage_supply
            leakage_return = project.get(duct_section, 'improved_leakage_return')
            iresults['leakage_return'] = leakage_return

            iresults = get_rest_results(settings, iresults, project)

            output_worksheet_g(iresults)            
        #endif
        
    #endfor               
    
    return results
#enddef

