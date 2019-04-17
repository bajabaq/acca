#---------------------------------------------------------------
# Worksheet B - Windows and Glass Doors
#---------------------------------------------------------------

import sys
from hvac_database import get_db_filename, do_query
from hvac_math import round_ctd

    
def get_slm(settings, latitude, direction):

    SQL = """SELECT slm FROM latitude_slm WHERE north_latitude = ? AND direction = ?"""    
    
    n_lat = round_ctd(latitude)
    dir   = get_dir(direction)
    
    SQL_vars = (n_lat,dir,)
    results = do_query(settings, SQL, SQL_vars)                
    slm_res = results[0]
    slm = slm_res[0]
    
    #there should only be one
    
    return slm
#enddef


def get_fenestration_performance(settings, construction_number, frame_type):
    SQL = """SELECT u, shgc FROM fenestration_performance WHERE construction_number = ? AND frame_type = ?"""    

    SQL_vars = (construction_number, frame_type,)
    results = do_query(settings, SQL, SQL_vars)                
        
    return results[0] #[u, shgc] = results[0]
#enddef


#see NOTE 1 on Worksheet B for factors
def get_htm_adjustment_heating(window_door_type):
    adjustment = 0.0    
    if window_door_type == 'default':
        adjustment = 1.0
    elif window_door_type == 'bay window':
        adjustment = 1.15
    elif window_door_type == 'garden window':        
        adjustment = 2.75
    elif window_door_type == 'french door':        
        adjustment = 0.70
    else:
        print("ERROR in get_htm_adjustment_heating - window_door_type (" + window_door_type + ") not found!!!")
        sys.exit()    
    #endif

    return adjustment
#enddef

#see NOTE 2 on Worksheet B for factors
#bay windows could have insect screens, but NOTE 2 does not address that, so leaving same for both cases
#garden windows do not have insect screens
#screens on french doors wouldn't make a lot of sense
def get_htm_adjustment_cooling(window_door_type, insect_screen):
    adjustment = 0.0
    if window_door_type == 'default' and insect_screen == 'none':
        adjustment = 1.0
    elif window_door_type == 'default' and insect_screen == 'full outdoor':
        adjustment = 0.80
    elif window_door_type == 'default' and insect_screen == 'half outdoor':
        adjustment = 0.90
    elif window_door_type == 'default' and insect_screen == 'full indoor':
        adjustment = 0.90
    elif window_door_type == 'default' and insect_screen == 'half indoor':
        adjustment = 0.95
    elif window_door_type == 'bay window':
        adjustment = 1.15    
    elif window_door_type == 'garden window':        
        adjustment = 2.00
    elif window_door_type == 'french door':        
        adjustment = 0.70
    else:
        print("ERROR in get_htm_adjustment_cooling - window_door_type not found!!!")
        sys.exit()    
    #endif

    return adjustment
#enddef

def get_dir(direction):
    if direction == 'NE' or direction == 'NW':
        dir = 'NE_or_NW'
    elif direction == 'E' or direction == 'W':
        dir = 'E_or_W'
    elif direction == 'SE' or direction == 'SW':
        dir = 'SE_or_SW'
    else:
        dir = direction
    #endif
    return dir
#enddef

def get_htm_cooling(construction_num, internal_shade, num_panes_thick, direction, ctd, settings):
        
    rounded_ctd = round_ctd(ctd) #for table 3 lookup, maybe should interpolate instead...
    
    glass_type = construction_num.split('-')[1]
    dire = get_dir(direction)    
    
    SQL_vars = (glass_type, internal_shade, str(num_panes_thick), dire, rounded_ctd,)    
    SQL = ''
    SQL = """SELECT htm FROM cooling_htm WHERE glass_type = ? AND shade = ? AND num_panes_thick = ? AND direction = ? AND ctd = ?"""
    results = do_query(settings, SQL, SQL_vars) 
                
    if len(results) < 1:
        print("htm_cooling query not found - come check the database")
        sys.exit()
    #endif
    htm_res = results[0]
    htm = htm_res[0]
    
    return htm
#enddef

def get_win(htd, ctd, latitude, direction, win_type_section, settings, project):
    #Window Info - from survey    
    num_panes_thick        = int(project.get(win_type_section, 'num_panes_thick'))      #2
    frame_type             = project.get(win_type_section, 'frame_type')                #mb
    construction_num       = project.get(win_type_section, 'construction_number')       #'1D-c' see table 2
    opening_height         = float(project.get(win_type_section, 'height'))             #4.5
    opening_width          = float(project.get(win_type_section, 'width'))              #4.0
    num_of_type            = int(project.get(win_type_section, 'num_of_type'))          #1
    height_to_overhang     = float(project.get(win_type_section, 'height_to_overhang')) #1.0
    overhang_width         = float(project.get(win_type_section, 'overhang_width'))     #1.5
    window_door_type       = project.get(win_type_section, 'window_door_type')          #default
    insect_screen          = project.get(win_type_section, 'insect_screen')             #full indoor
    internal_shade         = project.get(win_type_section, 'internal_shade')            #blinds
    
    [u_val, shgc]          = get_fenestration_performance(settings, construction_num, frame_type)
        
    heating_htm_unadjusted = u_val * htd
    heating_htm_adjustment = get_htm_adjustment_heating(window_door_type)
    heating_htm_adjusted   = heating_htm_unadjusted * heating_htm_adjustment
    
    cooling_htm_unadjusted = get_htm_cooling(construction_num, internal_shade, num_panes_thick, direction, ctd, settings)    #see tbl3
    cooling_htm_adjustment = get_htm_adjustment_cooling(window_door_type, insect_screen)
    cooling_htm_adjusted   = cooling_htm_unadjusted * cooling_htm_adjustment
    
    #print "here" 
    #print cooling_htm_adjusted
    
    area_of_opening        = opening_height * opening_width        
    net_area               = area_of_opening * num_of_type

  
    if direction not in ('N','NE','NW'):
        #opening_height                                               #H    
        #overhang_width                                               #X  - from survey
        #height_to_overhang                                           #Y  - from site survey
        slm           = get_slm(settings, latitude, direction)
        shade_line    = overhang_width * slm                          #Z        
        shaded_height = shade_line - height_to_overhang               #S
            
        #maybe leave this math alone and only worry about the output...
        if shaded_height <= 0:
            unshaded_height              = ''    
            cooling_htm_unadjusted_north = ''
            cooling_htm_adjusted_north   = ''    
            shaded_glass_factor          = ''
            unshaded_glass_factor        = ''    
            shaded_htm                   = ''
            unshaded_htm                 = ''            
            effective_htm                = cooling_htm_adjusted
        elif shaded_height > opening_height:
            unshaded_height              = ''        
            cooling_htm_unadjusted_north = get_htm_cooling(construction_num, internal_shade, num_panes_thick, 'N', ctd, settings)
            cooling_htm_adjusted_north   = cooling_htm_unadjusted_north * cooling_htm_adjustment        
            shaded_glass_factor          = ''
            unshaded_glass_factor        = ''        
            shaded_htm                   = ''
            unshaded_htm                 = ''        
            effective_htm                = cooling_htm_adjusted_north
        else:
            unshaded_height              = opening_height - shaded_height              #U            
            cooling_htm_unadjusted_north = get_htm_cooling(construction_num, internal_shade, num_panes_thick, 'N', ctd, settings)
            cooling_htm_adjusted_north   = cooling_htm_unadjusted_north * cooling_htm_adjustment
            
            shaded_glass_factor          = shaded_height   / opening_height
            unshaded_glass_factor        = unshaded_height / opening_height
            
            shaded_htm                   = cooling_htm_adjusted_north * shaded_glass_factor
            unshaded_htm                 = cooling_htm_adjusted       * unshaded_glass_factor
            
            effective_htm                = shaded_htm + unshaded_htm
        #endif
        
    else:
        opening_height               = opening_height
        overhang_width               = overhang_width
        slm                          = 1
        shade_line                   = 0
        height_to_overhang           = height_to_overhang
        shaded_height                = 0
        unshaded_height              = 0
        cooling_htm_unadjusted_north = 0
        cooling_htm_adjustment       = cooling_htm_adjustment
        cooling_htm_adjusted_north   = 0
        shaded_glass_factor          = 0
        unshaded_glass_factor        = 0
        shaded_htm                   = 0
        unshaded_htm                 = 0
        effective_htm                = cooling_htm_adjusted
    #endif

    heating_btuh = net_area * heating_htm_adjusted
    cooling_btuh = net_area * effective_htm

    #print net_area, heating_htm_adjusted, heating_btuh
    #print net_area, effective_htm, cooling_btuh

    
    win =  {'direction'                    : direction,
            'num_panes_thick'              : num_panes_thick,
            'frame_type'                   : frame_type,
            'construct_num'                : construction_num,
            'u_val'                        : u_val,                 
            'heating_htm_unadjusted'       : heating_htm_unadjusted,
            'heating_htm_adjustment'       : heating_htm_adjustment,
            'heating_htm_adjusted'         : heating_htm_adjusted,
            'cooling_htm_unadjusted'       : cooling_htm_unadjusted,
            'cooling_htm_adjustment'       : cooling_htm_adjustment,
            'cooling_htm_adjusted'         : cooling_htm_adjusted,
            'area_of_opening'              : area_of_opening,
            'num_of_these_windows'         : num_of_type,
            'net_area'                     : net_area,
            'H'                            : opening_height,
            'X'                            : overhang_width,
            'slm'                          : slm,
            'Z'                            : shade_line,
            'Y'                            : height_to_overhang,
            'S'                            : shaded_height,
            'U'                            : unshaded_height,
            'cooling_htm_unadjusted_north' : cooling_htm_unadjusted_north,
            'cooling_htm_adjustment'       : cooling_htm_adjustment,
            'cooling_htm_adjusted_north'   : cooling_htm_adjusted_north,
            'shaded_glass_factor'          : shaded_glass_factor,
            'unshaded_glass_factor'        : unshaded_glass_factor,
            'shaded_htm'                   : shaded_htm,
            'unshaded_htm'                 : unshaded_htm,
            'effective_htm'                : effective_htm,
            'heating_btuh'                 : heating_btuh,
            'cooling_btuh'                 : cooling_btuh
        }

    return win
#enddef


def output_worksheet_b(results):
    
    msg = ""
    msg = msg +  60 * "=" + "\n"
    msg = msg +  "Worksheet B: Heating and Cooling HTM and Load Area for Windows and Glass Doors" + "\n"
        
    for window in results:

        direction              = window['direction']
        num_panes_thick        = window['num_panes_thick']
        frame_type             = window['frame_type']
        construct_num          = window['construct_num']
        u_val                  = window['u_val']
        heating_htm_unadjusted = window['heating_htm_unadjusted']
        heating_htm_adjustment = window['heating_htm_adjustment']
        heating_htm_adjusted   = window['heating_htm_adjusted']
        cooling_htm_unadjusted = window['cooling_htm_unadjusted']
        cooling_htm_adjustment = window['cooling_htm_adjustment']
        cooling_htm_adjusted   = window['cooling_htm_adjusted']
        area_of_opening        = window['area_of_opening']
        num_of_these_windows   = window['num_of_these_windows']
        net_area               = window['net_area']
    
        msg = msg +  60 * "-"    + "\n"
        msg = msg +  "Direction             : %5s" % (direction) + "\n"
        msg = msg +  "Number of panes_thick : %5s"  % (num_panes_thick) + "\n"
        msg = msg +  "Frame Type            : %5s"  % (frame_type) + "\n"
        msg = msg +  " 1) Table 2A construction number               : %-10s"  % (construct_num) + "\n"
        msg = msg +  " 2) Table 2A U-value                           : %1.2f" % (u_val) + "\n"
        msg = msg +  " 3) Unadjusted heating HTM = U x HTD           : %3.2f" % (heating_htm_unadjusted) + "\n"
        msg = msg +  " 4) Heating HTM adjustment (see Note 1)        : %1.2f" % (heating_htm_adjustment) + "\n"
        msg = msg +  " 5) Adjusted heating HTM (L3 x L4)             : %3.2f" % (heating_htm_adjusted) + "\n"
        msg = msg +  " 6) Unadjusted cooling (from Table 3A)         : %3.2f" % (cooling_htm_unadjusted) + "\n"
        msg = msg +  " 7) Cooling HTM adjustment (see Note 2)        : %1.2f" % (cooling_htm_adjustment) + "\n"
        msg = msg +  " 8) Adjusted cooling HTM (L6 x L7)             : %3.2f" % (cooling_htm_adjusted) + "\n"
        msg = msg +  " 9) Area of opening (SqFt) for one unit        : %3.2f" % (area_of_opening) + "\n"
        msg = msg +  "10) Number of identical assemblies             : %2s"   % (num_of_these_windows) + "\n"
        msg = msg +  "11) Net area of identical assemblies (L9 x L10): %3.2f" % (net_area) + "\n"
        
        
        if direction not in ('N','NE','NW'):
            opening_height                  = window['H']
            overhang_len                    = window['X']
            slm                             = window['slm']
            shade_line                      = window['Z']
            height_top_opening_to_overhang  = window['Y']
            shaded_height                   = window['S']
            unshaded_height                 = window['U']
            cooling_htm_unadjusted_north    = window['cooling_htm_unadjusted_north']
            cooling_htm_adjustment          = window['cooling_htm_adjustment']
            cooling_htm_adjusted_north      = window['cooling_htm_adjusted_north']
            shaded_glass_factor             = window['shaded_glass_factor']
            unshaded_glass_factor           = window['unshaded_glass_factor']
            shaded_htm                      = window['shaded_htm']
            unshaded_htm                    = window['unshaded_htm']
            effective_htm                   = window['effective_htm']
            
            msg = msg +  "" + "\n"
            msg = msg +  "Overhang Adjustment" + "\n"
            msg = msg +  "12) Opening height (H) in ft                   : %2.2f" % (opening_height                ) + "\n"
            msg = msg +  "13) Overhang length (X) in ft                  : %3.2f" % (overhang_len                  ) + "\n"
            msg = msg +  "14) SLM value for local latitude               : %3.2f" % (slm                           ) + "\n"
            msg = msg +  "15) Shade line to OH (Z) = L13 x L14           : %3.3f" % (shade_line                    ) + "\n"
            msg = msg +  "16) Distance below OH (Y)                      : %3.2f" % (height_top_opening_to_overhang) + "\n"
            msg = msg +  "17) Shaded height                              : %3.3f" % (shaded_height                 ) + "\n"
            if shaded_height <= 0:
                msg = msg +  "18) Unshaded height (U)                        :" + "\n"
                msg = msg +  "19) North HTM from Table 3A                    :" + "\n"
                msg = msg +  "20) HTM adjustment (copy L7)                   :" + "\n"
                msg = msg +  "21) Adjusted North HTM (L19 x L20)             :" + "\n"
                msg = msg +  "22) Shaded glass factor = L17 / L12            :" + "\n"
                msg = msg +  "23) Unshaded glass factor = L18 / L12          :" + "\n"
                msg = msg +  "24) Shaded HTM = L21 x L22                     :" + "\n"
                msg = msg +  "25) Unshaded HTM = L8 x L23                    :" + "\n"
            elif shaded_height > opening_height:
                msg = msg +  "18) Unshaded height (U)                        :" + "\n"
                msg = msg +  "19) North HTM from Table 3A                    : %3.2f" % (cooling_htm_unadjusted_north  ) + "\n"
                msg = msg +  "20) HTM adjustment (copy L7)                   : %3.2f" % (cooling_htm_adjustment        ) + "\n"
                msg = msg +  "21) Adjusted North HTM (L19 x L20)             : %3.2f" % (cooling_htm_adjusted_north    ) + "\n"
                msg = msg +  "22) Shaded glass factor = L17 / L12            :" + "\n"
                msg = msg +  "23) Unshaded glass factor = L18 / L12          :" + "\n"
                msg = msg +  "24) Shaded HTM = L21 x L22                     :" + "\n"
                msg = msg +  "25) Unshaded HTM = L8 x L23                    :" + "\n"
            else:
                msg = msg +  "18) Unshaded height (U)                        : %3.2f" % (unshaded_height               ) + "\n"
                msg = msg +  "19) North HTM from Table 3A                    : %3.2f" % (cooling_htm_unadjusted_north  ) + "\n"
                msg = msg +  "20) HTM adjustment (copy L7)                   : %3.2f" % (cooling_htm_adjustment        ) + "\n"
                msg = msg +  "21) Adjusted North HTM (L19 x L20)             : %3.2f" % (cooling_htm_adjusted_north    ) + "\n"
                msg = msg +  "22) Shaded glass factor = L17 / L12            : %3.2f" % (shaded_glass_factor           ) + "\n"
                msg = msg +  "23) Unshaded glass factor = L18 / L12          : %3.2f" % (unshaded_glass_factor         ) + "\n"
                msg = msg +  "24) Shaded HTM = L21 x L22                     : %3.2f" % (shaded_htm                    ) + "\n"
                msg = msg +  "25) Unshaded HTM = L8 x L23                    : %3.2f" % (unshaded_htm                  ) + "\n"
            #endif
            
            msg = msg +  "26) Effective HTM = L24 + L25                  : %3.2f" % (effective_htm                 ) + "\n"
        #endif
    #endfor  
    msg = msg + 60 * "=" + "\n"
    print(msg)
#enddef


#------------------------------------------------------------------------------
#   Worksheet B: Heating and Cooling HTM and 
#                Load Area for Windows (flat, bay, or garden)
#                              Glass Doors (hinged, sliding, or French)
#------------------------------------------------------------------------------
def worksheet_b(settings, project, a_results):
    
    htd      = a_results['htd']
    ctd      = a_results['ctd']
    latitude = a_results['latitude']
    
    results = []
    
    num_zones = int(project.get('Zones', 'num_zones'))
    for zone in range (1, num_zones+1):        
        zone_section = 'Zone ' + str(zone)
        print(zone_section)
        
        num_ext_walls = int(project.get(zone_section, 'num_ext_walls'))
        for ext_wall in range (1, num_ext_walls + 1):
            ext_wall_section = zone_section + ' ExtWall ' + str(ext_wall)
            direction = project.get(ext_wall_section, 'direction')                 #'N'
            print(4*" " + ext_wall_section)
            
            num_window_types = int(project.get(ext_wall_section, 'num_window_types'))
            for window_type in range (1, num_window_types + 1):
                window_type_section = ext_wall_section + ' Window ' + str(window_type)
                print(8*' ' + window_type_section)
                
                win = get_win(htd, ctd, latitude, direction, window_type_section, settings, project)
                results.append(win)
                
            #endfor
        #endfor
    #endfor       
       
    output_worksheet_b(results)
    
    return results
#enddef

