

import sys

def output_design_info(results):

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
    
    msg = msg + 60 * "="
    msg = msg + 20 * " " + "Form J1ae "
    msg = msg +  5 * " " + "Abridged Edition of Manual J, 8th Edition"
    msg = msg + 60 * "-"
    msg = msg + "Project                              : " + project_name
    msg = msg + "City, State                          : " + city + ", " + state
    msg = msg + "Table 1A Latitude                    : %3s" % (latitude)
    msg = msg + "Table 1A Elevation                   : %3s" % (elevation)
    msg = msg + "Indoor Conditions"
    msg = msg + "    Heating DryBulb                  : %2s" % (indoor_heating_db)
    msg = msg + "    Cooling DryBulb                  : %2s" % (indoor_cooling_db)
    msg = msg + "    Cooling RH%%                      : %2s" % (indoor_cooling_rh)
    msg = msg + "Outdoor Design Conditions"
    msg = msg + "    99%% DryBulb                      : %2s" % (outdoor_99per_db)
    msg = msg + "     1%% DryBulb                      : %2s" % (outdoor_1per_db)
    msg = msg + "   Grains Difference                 : %2s" % (grains_diff)
    msg = msg + "         Daily Range                 : %2s" % (daily_range)
    msg = msg + "Heating temperature difference (HTD) : %2s" % (htd)
    msg = msg + "Cooling temperature difference (CTD) : %2s" % (ctd)
    msg = msg + "Table 10A ACF                        : %.2f" % (acf)
    #msg = msg + "Air Density                        = " + str(ad)
        
    msg = msg + 60 * "-"
    
    print(msg)
#enddef

def output_building_info_aux(panels):
    for p in panels:
        construct_num = p['construction_number']
        direction     = '' #p['direction']
        net_area      = p['net_area']
        heating_htm_adjusted = p['heating_htm']
        cooling_htm_adjusted = p['cooling_htm']
        
        print(str(construct_num)+"-"+str(direction) + "\t" + str(heating_htm_adjusted) + "\t\t" + str(cooling_htm_adjusted) + "\t\t" + str(net_area) + "\t\t" + str(heating_htm_adjusted * net_area) + "\t\t" + str(cooling_htm_adjusted * net_area))
        

#enddef

def output_building_info(results, panel_type):
    msg = ""
    msg = msg + 60 * "="
    msg = msg + "Panels - " + panel_type
    msg = msg + "Const_Number\tHeating HTM\tCooling HTM\tNet Area\tBtuh Heating\tBtuh Cooling"
    msg = msg + 60 * "-"

    if panel_type != 'Windows':
        doors       = results['doors']
        ag_walls    = results['ag_walls']
        p_walls     = results['p_walls']
        bg_walls    = results['bg_walls']
        ceilings    = results['ceilings']
        p_ceilings  = results['p_ceilings']
        floors      = results['floors']
        p_floors    = results['p_floors']

        output_building_info_aux(doors)
        output_building_info_aux(ag_walls)
        output_building_info_aux(p_walls)
        output_building_info_aux(bg_walls)
        output_building_info_aux(ceilings)
        output_building_info_aux(p_ceilings)
#        output_building_info_aux(floors)up0n        output_building_info_aux(p_floors)
        
    else:
    
        for window in results:

            direction              = window['direction']
            frame_type             = window['frame_type']
            construct_num          = window['construct_num']
            u_val                  = window['u_val']
            
            heating_htm_adjusted   = window['heating_htm_adjusted']
            cooling_htm_adjusted   = window['cooling_htm_adjusted']

            area_of_opening        = window['area_of_opening']
            net_area               = window['net_area']
            
            
            if direction not in ('N','NE','NW'):
                effective_htm                   = window['effective_htm']
                cooling_htm_adjusted = effective_htm
            #endif
            print(str(construct_num)+"-"+frame_type+"-"+str(direction) + "\t" + str(heating_htm_adjusted) + "\t\t" + str(cooling_htm_adjusted) + "\t\t" + str(net_area) + "\t\t" + str(heating_htm_adjusted * net_area) + "\t\t" + str(cooling_htm_adjusted * net_area))
        #endfor  
    #endif

#enddef





def get_data_glass(results):
    btuh_heating = 0
    btuh_cooling = 0
    for panel in results:
#        print(panel
#        print(panel['heating_btuh']
#        print(panel['cooling_btuh']

        btuh_heating = btuh_heating + panel['heating_btuh']
        btuh_cooling = btuh_cooling + panel['cooling_btuh']
    #endfor

    return btuh_heating, btuh_cooling
#enddef

def get_data_panels(results):
    btuh_heating = 0
    btuh_cooling = 0
    a = ('doors', 'ag_walls', 'p_walls', 'bg_walls', 'ceilings', 'p_ceilings', 'floors', 'p_floors')
    for p in a:  
        for panel in results[p]:
#            print(panel           
#            print(panel['heating_btuh'], panel['cooling_btuh']

            btuh_heating = btuh_heating + panel['heating_btuh']
            btuh_cooling = btuh_cooling + panel['cooling_btuh']
        #endfor
    #endfor        

    return btuh_heating, btuh_cooling
#enddef

def get_data_infil(results):
    btuh_heating        = results['infiltration_load_heating']
    btuh_cooling        = results['sens_infil_load_cooling']
    btuh_latent_cooling = results['lat_infil_load_cooling']

    return btuh_heating, btuh_cooling, btuh_latent_cooling
#enddef

def get_internal_gains(results):

    btuh_cooling = (
        results['occupant_sens_load']  +
        results['default_sens_load']   +
        results['adjust_sens_load']    +
        results['appliance_sens_load'] +
        results['plant_sens_load'] )

    btuh_latent_cooling = (
        results['occupant_lat_load'] +
        results['default_lat_load']  +
        results['adjust_lat_load']   +
        results['appliance_lat_load']+
        results['plant_lat_load'] )

#    print(btuh_cooling, btuh_latent_cooling
    
    return btuh_cooling, btuh_latent_cooling
#enddef

def get_data_duct(results, total_btuh_heating, total_btuh_cooling):
    btuh_heating        = total_btuh_heating * results['nhlf']
    btuh_cooling        = total_btuh_cooling * results['nsgf']
    btuh_latent_cooling = results['nlg']
    
#    print(results['nhlf'], btuh_heating, results['nsgf'], btuh_cooling, btuh_latent_cooling
    return btuh_heating, btuh_cooling, btuh_latent_cooling
#enddef


def form_j1ae(worksheet_results):
    a_results = worksheet_results['a']
    b_results = worksheet_results['b']
    c_results = worksheet_results['c']
    d_results = worksheet_results['d']
    e_results = worksheet_results['e']                        
    f_results = worksheet_results['f']  
    g_results = worksheet_results['g']
    h_results = worksheet_results['h']
    bhg_results = worksheet_results['bhg']
    

    total_btuh_heating = 0
    total_btuh_cooling = 0
    total_btuh_latent_cooling = 0
    
    btuh_heating, btuh_cooling = get_data_glass(b_results)
    total_btuh_heating = total_btuh_heating + btuh_heating
    total_btuh_cooling = total_btuh_cooling + btuh_cooling

    btuh_heating, btuh_cooling = get_data_glass(c_results)
    total_btuh_heating = total_btuh_heating + btuh_heating
    total_btuh_cooling = total_btuh_cooling + btuh_cooling

    btuh_heating, btuh_cooling = get_data_panels(d_results)
    total_btuh_heating = total_btuh_heating + btuh_heating
    total_btuh_cooling = total_btuh_cooling + btuh_cooling

    btuh_heating, btuh_cooling, btuh_latent_cooling = get_data_infil(e_results)
    total_btuh_heating = total_btuh_heating + btuh_heating
    total_btuh_cooling = total_btuh_cooling + btuh_cooling
    total_btuh_latent_cooling =  total_btuh_latent_cooling + btuh_latent_cooling
    
    btuh_cooling, btuh_latent_cooling = get_internal_gains(f_results)
    total_btuh_cooling = total_btuh_cooling + btuh_cooling
    total_btuh_latent_cooling = total_btuh_latent_cooling + btuh_latent_cooling

    print("14) Sub Totals: " + str('{0:.3f}'.format(total_btuh_heating)) + "   " + str('{0:.3f}'.format(total_btuh_cooling)) + "\n")

    btuh_heating, btuh_cooling, btuh_latent_cooling = get_data_duct(g_results, total_btuh_heating, total_btuh_cooling)
    total_btuh_heating = total_btuh_heating + btuh_heating
    total_btuh_cooling = total_btuh_cooling + btuh_cooling
    total_btuh_latent_cooling = total_btuh_latent_cooling + btuh_latent_cooling

    btuh_cooling       = bhg_results
    total_btuh_cooling = total_btuh_cooling + btuh_cooling


    print("15) Totals: Heating:" + str('{0:.3f}'.format(total_btuh_heating)) + "   Cooling:" + str('{0:.3f}'.format(total_btuh_cooling)) + " Latent Cool:" + str('{0:.3f}'.format(total_btuh_latent_cooling)) + "\n")
    
    
    
    
    sys.exit()
    
    output_design_info(a_results)
    output_building_info(b_results, 'Windows')
#    output_building_info(c_results, 'Skylights')
    output_building_info(d_results, 'Doors')
    output_infiltration_info(e_results)
    output_duct_info(g_results)

    


    
#enddef


def form_j1(worksheet_results):
    a_results = worksheet_results['a']
    b_results = worksheet_results['b']
    c_results = worksheet_results['c']
    d_results = worksheet_results['d']
    e_results = worksheet_results['e']                        
    f_results = worksheet_results['f']  
    g_results = worksheet_results['g']
    h_results = worksheet_results['h']

    print("not done yet")
#enddef
