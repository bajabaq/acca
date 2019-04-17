import math


import hvac_database
import load_calc_wksht_aux

def get_oa_ach(ag_vol):
    oa_ach = 0.35 * ag_vol / 60
    return oa_ach
#enddef

def get_ach(settings, ach_type, construction, floor_area):
    ach = 0

    SQL = """SELECT """ + ach_type + """ FROM air_change_value WHERE construction = ? AND floor_area <= ? ORDER BY floor_area DESC LIMIT 1"""
#    print(SQL)
    SQL_vars = (construction,floor_area)
    
    results = hvac_database.do_query(settings, SQL, SQL_vars)
    ach_res = results[0]
    ach     = ach_res[0]
#    print(ach)
    return ach  #get from table 5A
#enddef

def get_fireplace_cfm(settings, num_fireplaces, construction):
    SQL = """SELECT infiltration FROM fireplace_infiltration WHERE construction = ?"""
    SQL_vars = (construction,)
    
    results = hvac_database.do_query(settings, SQL, SQL_vars)
    cfm_res = results[0]
    cfm = cfm_res[0]

    if num_fireplaces == 2:
        cfm = cfm + 7
    elif num_fireplaces > 2:
        cfm = cfm + 10
    #endif

    return cfm
#enddef

def get_infiltration(params):

    ag_vol_h = float(params['conditioned_ag_vol_h'])
    ag_vol_c = float(params['conditioned_ag_vol_c'])
    
    results = params
    
    oa_ach_heating = get_oa_ach(ag_vol_h)
    oa_ach_cooling = get_oa_ach(ag_vol_c)
    oa_occupants   = 20 * params['num_occupants']
    oa_burners     = 0.5 * params['burner_capacity'] / 1000
    oa_max         = max(oa_ach_heating, oa_ach_cooling, oa_occupants, oa_burners)


    results['oa_ach_heating'] = oa_ach_heating
    results['oa_ach_cooling'] = oa_ach_cooling
    results['oa_occupants']   = oa_occupants
    results['oa_burners']     = oa_burners
    results['oa_max']         = oa_max

    #ENVELOPE INFILTRATION RATE
    envelope_leakage  = params['envelope_leakage']
    fireplace_leakage = params['fireplace_leakage']
    results['envelope_leakage']  = envelope_leakage
    results['fireplace_leakage'] = fireplace_leakage

    envelope_ach_heating = get_ach(params['settings'],'ach_heating', envelope_leakage, params['floor_area_heating']) 
    envelope_ach_cooling = get_ach(params['settings'],'ach_cooling', envelope_leakage, params['floor_area_cooling'])
    results['envelope_ach_heating'] = envelope_ach_heating
    results['envelope_ach_cooling'] = envelope_ach_cooling

    fireplace_cfm = get_fireplace_cfm(params['settings'],params['num_fireplaces'],fireplace_leakage)

    results['fireplace_cfm'] = fireplace_cfm

    #something wierd here    
    infiltration_heating = envelope_ach_heating * ag_vol_h / 60.0 + fireplace_cfm
    infiltration_cooling = envelope_ach_cooling * ag_vol_c / 60.0        
    results['infiltration_heating'] = infiltration_heating
    results['infiltration_cooling'] = infiltration_cooling

    #INFILTRATION LOADS
    acf = params['acf']
    htd = params['htd']
    ctd = params['ctd']
    grains_diff = params['grains_difference']
    
    infiltration_load_heating = 1.1  * acf * infiltration_heating * htd + fireplace_cfm
    sens_infil_load_cooling   = 1.1  * acf * infiltration_cooling * ctd
    lat_infil_load_cooling    = 0.68 * acf * infiltration_cooling * grains_diff

    results['infiltration_load_heating'] = infiltration_load_heating
    results['sens_infil_load_cooling']   = sens_infil_load_cooling
    results['lat_infil_load_cooling']    = lat_infil_load_cooling

    #Suggested Value for Engineered Ventilation CFM
    diff_fresh_air_infil_heat = oa_max - infiltration_heating
    diff_fresh_air_infil_cool = oa_max - infiltration_cooling
    max_diff = max(diff_fresh_air_infil_heat, diff_fresh_air_infil_cool)
    eng_vent = 0
    if max_diff > 0:
        eng_vent = max_diff
    #endif

    results['diff_fresh_air_infil_heat'] = diff_fresh_air_infil_heat
    results['diff_fresh_air_infil_cool'] = diff_fresh_air_infil_cool    
    results['eng_vent']                  = eng_vent
    
    return results
#enddef


def output_worksheet_e(results):
    msg = ""
    msg = msg +  60 * "=" + "\n"
    msg = msg +  "Worksheet E: Infiltration" + "\n"
    msg = msg +  60 * "-" + "\n"
    msg = msg +  "Input Data" + "\n"
    tab = 4
    msg = msg +  tab*' ' + "Heating Floor Area  : " + str(results['floor_area_heating']) + "\n"
    msg = msg +  tab*' ' + "Cooling Floor Area  : " + str(results['floor_area_cooling']) + "\n"
    msg = msg +  tab*' ' + "Heating AG Volume   : " + str(results['conditioned_ag_vol_h']) + "\n"
    msg = msg +  tab*' ' + "Cooling AG Volume   : " + str(results['conditioned_ag_vol_c']) + "\n"
    msg = msg +  '' + "\n"
    msg = msg +  tab*' ' + "Number Bedrooms     : " + str(results['num_bedrooms']) + "\n"
    msg = msg +  tab*' ' + "Number Occupants    : " + str(results['num_occupants']) + "\n"
    msg = msg +  tab*' ' + "Number Fireplaces   : " + str(results['num_fireplaces']) + "\n"
    msg = msg +  tab*' ' + "Burner Capacity     : " + str(results['burner_capacity']) + "\n"
    msg = msg +  '' + "\n"
    msg = msg +  tab*' ' + "HTD                 : " + str(results['htd']) + "\n"
    msg = msg +  tab*' ' + "CTD                 : " + str(results['ctd']) + "\n"
    msg = msg +  tab*' ' + "Grains Difference   : " + str(results['grains_difference']) + "\n"
    msg = msg +  tab*' ' + "Air Change Freq     : " + str(results['acf']) + "\n"
    msg = msg +  ''
    msg = msg +  'Outdoor Air requirement' + "\n"
    msg = msg +  ' 1a) Outdoor air CFM for 0.35 ACH requirement heating: ' + str(results['oa_ach_heating']) + "\n"
    msg = msg +  ' 1b) Outdoor air CFM for 0.35 ACH requirement cooling: ' + str(results['oa_ach_cooling']) + "\n"
    msg = msg +  ' 2) Outdoor air CFM for occupants           : ' + str(results['oa_occupants']) + "\n"
    msg = msg +  ' 3) Outdoor air CFM for burners             : ' + str(results['oa_burners']) + "\n"
    msg = msg +  ' 4) Suggested value for fresh air CFM       : ' + str(results['oa_max']) + "\n"
    msg = msg +  '' + "\n"
    msg = msg +  'Envelope Infiltration Rate' + "\n"
    msg = msg +  ' 5) Tightness of construction      Envelope: ' + results['envelope_leakage'] + "\n"
    msg = msg +  '                               Fireplace(s): ' + results['fireplace_leakage']  + '      Num of fireplaces: ' + str(results['num_fireplaces']) + " Fireplace CFM: " + str(results['fireplace_cfm'])+ "\n"

    msg = msg +  ' 6) ACH for heating                        : Envelope ACH (heat) ' + str(results['envelope_ach_heating']) + "\n"
    msg = msg +  ' 7) ACH for cooling                        : Envelope ACH (cool) ' + str(results['envelope_ach_cooling']) + "\n"
    msg = msg +  ' 8) Infiltration CFM for heating           : ' + str(results['infiltration_heating']) + "\n"
    msg = msg +  ' 9) Infiltration CFM for cooling           : ' + str(results['infiltration_cooling']) + "\n"
    msg = msg +  '' + "\n"
    msg = msg +  'Infiltration Loads' + "\n"
    msg = msg +  '10) Infiltration load for heating          : ' + str(results['infiltration_load_heating']) + "\n"
    msg = msg +  '11) Sensible infiltration load for cooling : ' + str(results['sens_infil_load_cooling']) + "\n"
    msg = msg +  '12) Latent infiltration load for cooling   : ' + str(results['lat_infil_load_cooling']) + "\n"
    msg = msg +  '' + "\n"
    msg = msg +  'Suggested Value for Engineered Ventilation CFM' + "\n"
    msg = msg +  '13a) Difference in Fresh Air CFM - Heating Infiltration CFM (L4 - L8): ' + str(results['diff_fresh_air_infil_heat']) + "\n"
    msg = msg +  '13b) Difference in Fresh Air CFM - Cooling Infiltration CFM (L4 - L9): ' + str(results['diff_fresh_air_infil_cool']) + "\n"
    msg = msg +  '14) Suggested value for engineered ventilation CFM : ' + str(results['eng_vent']) + "\n" 
    msg = msg +  60 * "=" + "\n"
    print(msg)
    
#enddef


#------------------------------------------------------------------------------
#   Worksheet E: Infiltration
#------------------------------------------------------------------------------
def worksheet_e(settings, project, a_results):

    htd               = a_results['htd']
    ctd               = a_results['ctd']
    acf               = a_results['acf']
    grains_difference = a_results['grains_diff']

    num_bedrooms   = project.getint('Internal', 'num_bedrooms')
    num_occupants  = project.getint('Internal', 'num_occupants')
    num_fireplaces = project.getint('Internal', 'num_fireplaces')

    #see pg 177 on how to deal with fireplaces
    envelope_leakage  = project.get('Internal', 'envelope_leakage')
    fireplace_leakage = project.get('Internal', 'fireplace_leakage')

    floor_area_heating = 0
    floor_area_cooling = 0

    #this worksheet isn't correct - what if you have more than 1 zone (or system)
    #probably need to bring in the params and get_infiltration into the for-loop

    num_zones = int(project.get('Zones', 'num_zones'))
    for zone in range (1, num_zones+1):        
        zone_section = 'Zone ' + str(zone)
        print(zone_section)

        floor_area_heating = floor_area_heating + load_calc_wksht_aux.get_conditioned_floor_area(project, zone_section, 'heated')
        #results['floor_area_heating'] = floor_area_heating
        floor_area_cooling = floor_area_cooling +  load_calc_wksht_aux.get_conditioned_floor_area(project,zone_section,'cooled')
        #results['floor_area_cooling'] = floor_area_cooling
        
        if floor_area_heating != floor_area_cooling:
            print("WARNING!!! heating and cooling floor areas differ - assumptions below may be wrong!!!!")
            sys.exit()
        #endif

        #walls in zone
        num_ext_walls = project.getint(zone_section,'num_ext_walls')
        all_height = 0
        all_lengths = []
        for wall in range(1,num_ext_walls+1):
            wall_section = zone_section + ' ExtWall ' + str(wall)

            height = project.getfloat(wall_section, 'height')            
            all_lengths.append(project.getfloat(wall_section, 'length'))
            all_height = all_height + height
        #endfor
        avg_height = all_height / num_ext_walls

        min_len = min(all_lengths)
        max_len = max(all_lengths)
        #print(max_len)
        
        #probably have to figure out what to do in case of partition ceilings
        #ceilings in zone
        num_ceilings = project.getint(zone_section,'num_ceilings')
        for ceiling in range(1,num_ceilings+1):
            ceiling_section = zone_section + ' Ceiling ' + str(ceiling)

            slope = project.getfloat(ceiling_section, 'slope')

        #endfor

        ceiling_volume = 0
        if slope > 0: #we have a cathedral ceiling, add this volume to the zone_volume
            pi = 3.1415
            peak_height_above_floor =  project.getfloat(ceiling_section, 'peak_height_above_floor')            

            cv_height = peak_height_above_floor - avg_height
            area = 1/2 * min_len * cv_height
            ceiling_volume = area * max_len
            #print(height)
            print(area)
            print(ceiling_volume)


        #endif            
        #print(floor_area_heating*height)
        #print(ceiling_volume)

        zone_volume = floor_area_heating * avg_height + ceiling_volume #(project 8 is 26100 vs 14400)
        print(zone_volume)

        #see worksheet_g for floor_area_heating and cooling data
        params = {
            'settings'            : settings,
            'project'             : project,
            'floor_area_heating'  : floor_area_heating,
            'floor_area_cooling'  : floor_area_cooling,
            'conditioned_ag_vol_h': zone_volume,
            'conditioned_ag_vol_c': zone_volume,
            'num_bedrooms'        : num_bedrooms,
            'num_occupants'       : num_occupants,
            'num_fireplaces'      : num_fireplaces,
            'burner_capacity'     : 0,
            'htd'                 : htd,
            'ctd'                 : ctd,
            'grains_difference'   : grains_difference,
            'acf'                 : acf,
            'envelope_leakage'    : envelope_leakage,
            'fireplace_leakage'   : fireplace_leakage,
        }

        results = get_infiltration(params)
        output_worksheet_e(results)
    #end for


    return results
#enddef


