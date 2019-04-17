
import math
import sys

import hvac_database
import hvac_math

def get_u_val(settings, construction_number):
#    print(construction_number)

    SQL = """SELECT u_val, group_num FROM opaque_panel_performance_u WHERE construction_number = ?"""    
        
    SQL_vars = (construction_number,)
    results  = hvac_database.do_query(settings, SQL, SQL_vars)                
    #print(results)    

    if len(results) < 1:
        print("none found, come update u_val table")
        sys.exit()
    else:
        u_val_res = results[0]
    #endif
    return u_val_res
#enddef

#so don't have to type as much we're assigning a fake-group number in the get_uval query
#except for the 19-heat construction codes (those don't come in here anyway)
#for construction numbers 11, 16-22
def get_cltd_4a(settings, group_num, ctd, daily_range):
    SQL = """SELECT cltd FROM opaque_panel_performance_cltd WHERE group_num = ? AND ctd = ? AND daily_range = ?"""
    SQL_vars = (group_num,ctd,daily_range,)
    
    results = hvac_database.do_query(settings, SQL, SQL_vars)                
    
    cltd = 44444
    if len(results) < 1:
        print("none found, come update cltd table - cltd_4a")
        sys.exit()
    elif len(results) > 1:
        print("too many found, come update query - cltd_4a")
        sys.exit()
    else:
        cltd_res = results[0]
        cltd     = cltd_res[0]
    #endif
    return cltd
#enddef

#for construction numbers 12-15
def get_cltd_4b(settings, group_num, construction, ctd, daily_range):
    SQL = """SELECT cltd FROM opaque_panel_performance_cltd WHERE group_num = ? AND construction = ? AND ctd = ? AND daily_range = ?"""
    SQL_vars = (group_num,construction,ctd,daily_range,)
    
    results = hvac_database.do_query(settings, SQL, SQL_vars)                
    
    cltd = 44444
    if len(results) < 1:
        print("none found, come update cltd table - cltd_4b")
        sys.exit()
    elif len(results) > 1:
        print("too many found, come update query - cltd_4b")
        sys.exit()
    else:
        cltd_res = results[0]
        cltd     = cltd_res[0]
    #endif
    return cltd
#enddef

def get_cltd(settings, group_num, rounded_ctd, daily_range, panel_subtype):
    print(group_num, rounded_ctd, daily_range, panel_subtype)
    #input("x")
    #sys.exit()
    if panel_subtype == 'partition':
        SQL = """SELECT cltd FROM opaque_panel_performance_cltd WHERE group_num = ? AND ctd = ? AND daily_range = ? AND construction_number = 'partition'"""
        SQL_vars = (group_num,rounded_ctd,daily_range,)
    elif len(panel_subtype) > 0: #has something other than partition - like above_grade or below_grade 
        SQL = """SELECT cltd FROM opaque_panel_performance_cltd WHERE group_num = ? AND ctd = ? AND daily_range = ? AND (construction_number = 'wall' OR construction_number = '22')"""
        SQL_vars = (group_num,rounded_ctd,daily_range,)
    else:
        SQL = """SELECT cltd FROM opaque_panel_performance_cltd WHERE group_num = ? AND ctd = ? AND daily_range = ?"""
        SQL_vars = (group_num,rounded_ctd,daily_range,)
    #endif    
    
    results = hvac_database.do_query(settings, SQL, SQL_vars)                
    #print SQL, SQL_vars
    #for res in results:
    #    print res
    
    cltd = 44444
    if len(results) < 1:
        print("none found, come update cltd table")
    elif len(results) > 1:
        print("too many found, come update query")
    else:
        cltd_res = results[0]
        cltd     = cltd_res[0]
    #endif
    #print cltd
    return cltd
#enddef


def get_ptdh(settings, construction_number, rounded_htd):
    print(construction_number,rounded_htd)
    SQL = """SELECT ptdh FROM opaque_panel_performance_ptdh WHERE construction_number = ? AND htd = ?"""
    SQL_vars = (construction_number,rounded_htd)
    
    results = hvac_database.do_query(settings, SQL, SQL_vars)                
    
    ptdh = 77777
    if len(results) < 1:
        print("none found, come update ptdh table")
        sys.exit()
    elif len(results) > 1:
        print("too many found, come update query")
        sys.exit()
    else:
        ptdh_res = results[0]
        ptdh     = ptdh_res[0]
    #endif

    return ptdh
#enddef


def get_opaque_panel(params):
    print(8*' ' + 'in get_opaque_panel........')
    
    settings    = params['settings']
    section     = params['section']    
    project     = params['project']
    htd         = params['htd']
    ctd         = params['ctd']
    rounded_ctd = params['rounded_ctd']
    daily_range = params['daily_range']
    panel_type  = params['panel_type']
    
    construction_number = project.get(section, 'construction_number')
    insulation          = 0
    insulation_code     = ''    
    construction_code   = ''
    if panel_type == 'ext_wall':    
        insulation        = int(project.get(section, 'board_insulation'))
        exterior_material = project.get(section, 'exterior_material')
        framing_material  = project.get(section, 'framing_material')
        construction_code = exterior_material + framing_material
    elif panel_type == 'floor' or panel_type == 'p_floor':
        insulation              = int(project.get(section, 'insulation'))        
        floor_construction_code = project.get(section, 'floor_construction_code')
        soil_condition_code     = project.get(section, 'soil_condition_code')
        if soil_condition_code == "NA":
            soil_condition_code = ""
        #endif
        construction_code       = floor_construction_code + soil_condition_code        
    elif panel_type == 'ceiling':
        insulation              = int(project.get(section, 'insulation'))        
    #elif panel_type == 'door':
    #    insulation              = 0
    #endif

    if insulation >= 0 :
        insulation_code = '-' + str(insulation)
    else:
        if len(construction_code) > 0:
            insulation_code = '-'
        #endif
    #endif
    construction_number = construction_number + insulation_code + construction_code
    print(construction_number)
    

    slope = 0.0
    if panel_type == 'door':
        direction = params['direction']
        percent_area_glass = float(project.get(section,'percent_area_glass'))
        if percent_area_glass > 0.51:
            print("This door should actually be classified as a 'French Door' - use in Wksht A")
            sys.exit()
        #endif
        area_of_openings = 0
    elif panel_type == 'ceiling' or panel_type == 'p_ceiling':
        if project.has_option(section, 'slope'):
            slope = float(project.get(section, 'slope'))
        else:
            print("Error - ceilings have to have slopes")
            sys.exit()
        #endif
        area_of_openings = 0  #fixme - have to loop over skylights
    elif panel_type == 'ext_wall':
        area_of_openings = 0.0

        num_door_types   = int(project.get(section, 'num_door_types'))
        num_window_types = int(project.get(section, 'num_window_types'))
        for door_type in range(1, num_door_types + 1):
            door_section = section + ' Door ' + str(door_type)
            width  = float(project.get(door_section, 'length'))
            height = float(project.get(door_section, 'height'))
            area = width * height
            area_of_openings = area_of_openings + area
        #endfor        
        for window_type in range(1, num_window_types + 1):
            window_section = section + ' Window ' + str(window_type)
            width  = float(project.get(window_section, 'width'))
            height = float(project.get(window_section, 'height'))
            number = float(project.get(window_section, 'num_of_type'))
            area = width * height * number
            area_of_openings = area_of_openings + area
        #endfor
#        print area_of_openings        
    elif panel_type == 'floor' or panel_type == 'p_floor': 
        area_of_openings = 0                          #assuming there are no holes in the floor
    #endif    
        
    length = float(project.get(section, 'length'))
    
    h_or_w = 'height'
    if (("Ceiling" in section) or ("Floor" in section)):
        h_or_w = 'width'
    #endif
    height_or_width     = project.getfloat(section, h_or_w)
    
    gross_area          = length * height_or_width / (math.cos(math.radians(slope)))
    net_area            = gross_area - area_of_openings

    net_or_exposed      = net_area
    
    exposed_slab = ''
    if "22" in construction_number:
        exposed_slab = 2 * (length + height_or_width)
        net_or_exposed = exposed_slab
    #endif
        
    #get U_val, CLTD from (Table 4A join on Table 4B by Group Val...) using ctd and daily_range (wksheetA)
    print(rounded_ctd)
    print(daily_range)
        
    panel_subtype   = ''
    if project.has_option(section, 'floor_type'):
        panel_subtype = project.get(section, 'floor_type')
    elif project.has_option(section, 'wall_type'):
        panel_subtype = project.get(section, 'wall_type')
    #endif
    
    print("here xxx")

    #if Floor over Enclosed Unconditioned Crawl Space or Basement
    if construction_number[:2] == "19":
        construction_number_heat = construction_number + "-heat"
        [u_val, group_num] = get_u_val(settings, construction_number_heat)
        rounded_htd = hvac_math.round_htd(htd)

        htd_or_ptdh  = get_ptdh(settings, construction_number, rounded_htd)
        heating_htm = u_val * htd_or_ptdh

        construction_number_cool = construction_number + "-cool"
        [u_val, group_num] = get_u_val(settings, construction_number_cool)
        print(construction_number_cool)
        print(u_val, group_num)

        cltd_or_ptdc  = get_cltd_4a(settings, group_num, rounded_ctd, daily_range)

        cooling_htm = u_val * cltd_or_ptdc
        print(cooling_htm)
#        sys.exit()
    else:
        print("here yyy")
        [u_val, group_num] = get_u_val(settings, construction_number)
    
        print(group_num, panel_subtype)

        if int(construction_number[:2]) in [12,13,14,15]:
            if panel_subtype is not 'partition':
                construction = 'wall'
            else:
                construction = 'partition'
            #endif

            cltd  = get_cltd_4b(settings, group_num, construction, rounded_ctd, daily_range)
        else:
            cltd  = get_cltd_4a(settings, group_num, rounded_ctd, daily_range)
        #endif
        
        htd_or_ptdh  = htd  #FIXME - ptdh = htd for vatilo residence...
        cltd_or_ptdc = cltd #get_cltd returns cltd or ptdc depending on panel_subtype (partition)

        heating_htm = u_val * htd_or_ptdh
        cooling_htm = u_val * cltd_or_ptdc
    #endif

    heating_btuh = net_or_exposed * heating_htm
    cooling_btuh = net_or_exposed * cooling_htm

    print( "HERE")
    print(net_or_exposed, heating_htm, heating_btuh)
    print(net_or_exposed, cooling_htm, cooling_btuh)

    results = {
        'construction_number' : construction_number,
        'length'              : length,        
        'height_or_width'     : height_or_width,
        'gross_area'          : gross_area,
        'area_of_openings'    : area_of_openings,
        'net_area'            : net_area,
        'exposed_slab'        : exposed_slab,
        'u_val'               : u_val,
        'htd_or_ptdh'         : htd_or_ptdh,
        'heating_htm'         : heating_htm,
        'group_letter'        : group_num,
        'cltd_or_ptdc'        : cltd_or_ptdc,
        'cooling_htm'         : cooling_htm,        
        'heating_btuh'        : heating_btuh,
        'cooling_btuh'        : cooling_btuh,
    }
    
    if "Door" in section:
        results['direction'] = direction
    #endif
    
    if project.has_option(section, 'wall_type'):
        results['wall_type'] = project.get(section, 'wall_type')
    #endif
    
    if project.has_option(section, 'slope'):
        results['slope'] = project.get(section, 'slope')
    #endif
    
    
    return results
#enddef

    

def output_worksheet_d(results):
    htd         = results['htd']
    ctd         = results['ctd']
    rounded_ctd = results['rounded_ctd']
    daily_range = results['daily_range']

    doors       = results['doors']
    ag_walls    = results['ag_walls']
    p_walls     = results['p_walls']
    bg_walls    = results['bg_walls']
    ceilings    = results['ceilings']
    p_ceilings  = results['p_ceilings']
    floors      = results['floors']
    p_floors    = results['p_floors']

    msg = ""
    msg = msg +  60 * "=" + "\n"
    msg = msg +  "Worksheet D: Opaque Panels (Wood and Metal Doors, Walls, Ceilings, Roofs and Floors" + "\n"
    msg = msg +  60 * "-" + "\n"
    msg = msg +  "HTD: " + str(htd) + " | CTD for Table 4 CLTD lookup: " + str(rounded_ctd) + "\n"
    msg = msg +  "CTD: " + str(ctd) + " |     Daily range for Table 4: " + str(daily_range) + "\n"

    sw = 5
    
    msg = msg +  "  7) Wood and Metal Doors" + "\n"
    for door in doors:
        msg = msg +  sw*' ' + 'Construction Number: ' + door['construction_number'] + "\n"
        msg = msg +  sw*' ' + 'Direction          : ' + door['direction'] + "\n"
        msg = msg +  sw*' ' + 'Width              : ' + str(door['length']) + "\n"
        msg = msg +  sw*' ' + 'Height             : ' + str(door['height_or_width']) + "\n"
        msg = msg +  sw*' ' + 'Gross Area         : ' + str(door['gross_area']) + "\n"
#        msg = msg +  sw*' ' + 'Area of Openings   : ' + str(door['area_of_openings']) + "\n"
        msg = msg +  sw*' ' + 'Net Area           : ' + str(door['net_area']) + "\n"
        msg = msg +  sw*' ' + 'U-Value            : ' + str(door['u_val']) + "\n"
        msg = msg +  sw*' ' + 'HTD                : ' + str(door['htd_or_ptdh']) + "\n"
        msg = msg +  sw*' ' + 'Heating HTM        : ' + str(door['heating_htm']) + "\n"
        msg = msg +  sw*' ' + 'CLTD               : ' + str(door['cltd_or_ptdc']) + "\n"
        msg = msg +  sw*' ' + 'Cooling HTM        : ' + str(door['cooling_htm']) + "\n"
        msg = msg +  '' + "\n"
    #endfor
    
    msg = msg +  "  8) Above Grade Walls" + "\n"
    for ag_wall in ag_walls:
        msg = msg +  sw*' ' + 'Construction Number: ' + ag_wall['construction_number'] + "\n"
        msg = msg +  sw*' ' + 'Length             : ' + str(ag_wall['length']) + "\n"
        msg = msg +  sw*' ' + 'Height             : ' + str(ag_wall['height_or_width']) + "\n"
        msg = msg +  sw*' ' + 'Gross Area         : ' + str(ag_wall['gross_area']) + "\n"
        msg = msg +  sw*' ' + 'Area of Openings   : ' + str(ag_wall['area_of_openings']) + "\n"
        msg = msg +  sw*' ' + 'Net Area           : ' + str(ag_wall['net_area']) + "\n"
        msg = msg +  sw*' ' + 'U-Value            : ' + str(ag_wall['u_val']) + "\n"
        msg = msg +  sw*' ' + 'HTD                : ' + str(ag_wall['htd_or_ptdh']) + "\n"
        msg = msg +  sw*' ' + 'Heating HTM        : ' + str(ag_wall['heating_htm']) + "\n"
        msg = msg +  sw*' ' + 'CLTD               : ' + str(ag_wall['cltd_or_ptdc']) + "\n"
        msg = msg +  sw*' ' + 'Cooling HTM        : ' + str(ag_wall['cooling_htm']) + "\n"
        msg = msg +  '' + "\n"
    #endfor
    msg = msg +  "  8) Partition Walls" + "\n"
    for p_wall in p_walls:
        msg = msg +  sw*' ' + 'Construction Number: ' + p_wall['construction_number']
        msg = msg +  sw*' ' + 'Length             : ' + str(p_wall['length'])
        msg = msg +  sw*' ' + 'Height             : ' + str(p_wall['height_or_width'])
        msg = msg +  sw*' ' + 'Gross Area         : ' + str(p_wall['gross_area'])
        msg = msg +  sw*' ' + 'Area of Openings   : ' + str(p_wall['area_of_openings'])
        msg = msg +  sw*' ' + 'Net Area           : ' + str(p_wall['net_area'])
        msg = msg +  sw*' ' + 'U-Value            : ' + str(p_wall['u_val'])
        msg = msg +  sw*' ' + 'PTDH               : ' + str(p_wall['htd_or_ptdh'])
        msg = msg +  sw*' ' + 'Heating HTM        : ' + str(p_wall['heating_htm'])
        msg = msg +  sw*' ' + 'PTDC               : ' + str(p_wall['cltd_or_ptdc'])
        msg = msg +  sw*' ' + 'Cooling HTM        : ' + str(p_wall['cooling_htm'])
        msg = msg +  ''
    #endfor
    msg = msg +  "  9) Below Grade Walls" + "\n"
    for bg_wall in bg_walls:
        msg = msg +  sw*' ' + 'Construction Number: ' + bg_wall['construction_number']
        msg = msg +  sw*' ' + 'Length             : ' + str(bg_wall['length'])
        msg = msg +  sw*' ' + 'Height             : ' + str(bg_wall['height_or_width'])
        msg = msg +  sw*' ' + 'Gross Area         : ' + str(bg_wall['gross_area'])
        msg = msg +  sw*' ' + 'Area of Openings   : ' + str(bg_wall['area_of_openings'])
        msg = msg +  sw*' ' + 'Net Area           : ' + str(bg_wall['net_area'])
        msg = msg +  sw*' ' + 'U-Value            : ' + str(bg_wall['u_val'])
        msg = msg +  sw*' ' + 'HTD                : ' + str(bg_wall['htd_or_ptdh'])
        msg = msg +  sw*' ' + 'Heating HTM        : ' + str(bg_wall['heating_htm'])
        msg = msg +  sw*' ' + 'CLTD               : ' + str(bg_wall['cltd_or_ptdc'])
        msg = msg +  sw*' ' + 'Cooling HTM        : ' + str(bg_wall['cooling_htm'])
        msg = msg +  ''
    #endfor

    msg = msg +  " 10) Ceilings" + "\n"
    for ceiling in ceilings:
        msg = msg +  sw*' ' + 'Construction Number: ' + ceiling['construction_number'] + "\n"
        msg = msg +  sw*' ' + 'Slope              : ' + str(ceiling['slope']) + "\n"
        msg = msg +  sw*' ' + 'Length             : ' + str(ceiling['length']) + "\n"
        msg = msg +  sw*' ' + 'Width              : ' + str(ceiling['height_or_width']) + "\n"
        msg = msg +  sw*' ' + 'Gross Area         : ' + str(ceiling['gross_area']) + "\n"
        msg = msg +  sw*' ' + 'Area of Openings   : ' + str(ceiling['area_of_openings']) + "\n"
        msg = msg +  sw*' ' + 'Net Area           : ' + str(ceiling['net_area']) + "\n"
        msg = msg +  sw*' ' + 'U-Value            : ' + str(ceiling['u_val']) + "\n"
        msg = msg +  sw*' ' + 'HTD                : ' + str(ceiling['htd_or_ptdh']) + "\n"
        msg = msg +  sw*' ' + 'Heating HTM        : ' + str(ceiling['heating_htm']) + "\n"
        msg = msg +  sw*' ' + 'CLTD               : ' + str(ceiling['cltd_or_ptdc']) + "\n"
        msg = msg +  sw*' ' + 'Cooling HTM        : ' + str(ceiling['cooling_htm']) + "\n"
        msg = msg +  '' + "\n"
    #endfor
    msg = msg +  " 10) Partition Ceilings - use PTD-H and PTD-C" + "\n"
    for p_ceiling in p_ceilings:
        msg = msg +  sw*' ' + 'Construction Number: ' + ceiling['construction_number'] + "\n"
        msg = msg +  sw*' ' + 'Slope              : ' + str(ceiling['slope']) + "\n"
        msg = msg +  sw*' ' + 'Length             : ' + str(ceiling['length']) + "\n"
        msg = msg +  sw*' ' + 'Width              : ' + str(ceiling['height_or_width']) + "\n"
        msg = msg +  sw*' ' + 'Gross Area         : ' + str(ceiling['gross_area']) + "\n"
        msg = msg +  sw*' ' + 'Area of Openings   : ' + str(ceiling['area_of_openings']) + "\n"
        msg = msg +  sw*' ' + 'Net Area           : ' + str(ceiling['net_area']) + "\n"
        msg = msg +  sw*' ' + 'U-Value            : ' + str(ceiling['u_val']) + "\n"
        msg = msg +  sw*' ' + 'PTDH               : ' + str(ceiling['htd_or_ptdh']) + "\n"
        msg = msg +  sw*' ' + 'Heating HTM        : ' + str(ceiling['heating_htm']) + "\n"
        msg = msg +  sw*' ' + 'PTDC               : ' + str(ceiling['cltd_or_ptdc']) + "\n"
        msg = msg +  sw*' ' + 'Cooling HTM        : ' + str(ceiling['cooling_htm']) + "\n"
        msg = msg +  '' + "\n"
    #endfor
    msg = msg +  "11A) Passive Floors (construction num 20,21,22)" + "\n"
    for floor in floors:
        msg = msg +  sw*' ' + 'Construction Number: ' + floor['construction_number'] + "\n"
        msg = msg +  sw*' ' + 'Length             : ' + str(floor['length']) + "\n"
        msg = msg +  sw*' ' + 'Width              : ' + str(floor['height_or_width']) + "\n"
        msg = msg +  sw*' ' + 'Gross Area         : ' + str(floor['gross_area']) + "\n"
        msg = msg +  sw*' ' + 'Area of Openings   : ' + str(floor['area_of_openings']) + "\n"
        msg = msg +  sw*' ' + 'Net Area           : ' + str(floor['net_area']) + "\n"
        msg = msg +  sw*' ' + 'Exposed Slab Edge  : ' + str(floor['exposed_slab']) + "\n"
        msg = msg +  sw*' ' + 'U-Value            : ' + str(floor['u_val']) + "\n"
        msg = msg +  sw*' ' + 'HTD                : ' + str(floor['htd_or_ptdh']) + "\n"
        msg = msg +  sw*' ' + 'Heating HTM        : ' + str(floor['heating_htm']) + "\n"
        msg = msg +  sw*' ' + 'CLTD               : ' + str(floor['cltd_or_ptdc']) + "\n"
        msg = msg +  sw*' ' + 'Cooling HTM        : ' + str(floor['cooling_htm']) + "\n"
        msg = msg +  '' + "\n"
    #endfor
    msg = msg +  "11A) Partition Floors (construction num 19) - use PTD-H and PTD-C" + "\n"
    for p_floor in p_floors:
        msg = msg +  sw*' ' + 'Construction Number: ' + p_floor['construction_number'] + "\n"
        msg = msg +  sw*' ' + 'Length             : ' + str(p_floor['length']) + "\n"
        msg = msg +  sw*' ' + 'Width              : ' + str(p_floor['height_or_width']) + "\n"
        msg = msg +  sw*' ' + 'Gross Area         : ' + str(p_floor['gross_area']) + "\n"
        msg = msg +  sw*' ' + 'Area of Openings   : ' + str(p_floor['area_of_openings']) + "\n"
        msg = msg +  sw*' ' + 'Net Area           : ' + str(p_floor['net_area']) + "\n"
        msg = msg +  sw*' ' + 'Exposed Slab Edge  : ' + str(p_floor['exposed_slab']) + "\n"
        msg = msg +  sw*' ' + 'U-Value            : ' + str(p_floor['u_val']) + "\n"
        msg = msg +  sw*' ' + 'PTDH               : ' + str(p_floor['htd_or_ptdh']) + "\n"
        msg = msg +  sw*' ' + 'Heating HTM        : ' + str(p_floor['heating_htm']) + "\n"
        msg = msg +  sw*' ' + 'PTDC               : ' + str(p_floor['cltd_or_ptdc']) + "\n"
        msg = msg +  sw*' ' + 'Cooling HTM        : ' + str(p_floor['cooling_htm']) + "\n"
        msg = msg +  '' + "\n"
    #endfor
    msg = msg +  60 * "=" + "\n"
    print(msg)
#enddef


#------------------------------------------------------------------------------
#   Worksheet D: Opaque Panels (Wood and Metal Doors, Walls, Ceilings, Roofs and Floors)
#------------------------------------------------------------------------------
def worksheet_d(settings, project, a_results):
        
    htd         = a_results['htd']
    ctd         = a_results['ctd']
    rounded_ctd = hvac_math.round_ctd(ctd) #for table 4 lookup
    daily_range = a_results['daily_range']
    
    doors       = []
    ag_walls    = []
    p_walls     = []
    bg_walls    = []
    ceilings    = []
    p_ceilings  = []
    floors      = []
    p_floors    = []
    
    params               = {}
    params['settings']   = settings
    params['project']    = project
    params['htd']        = htd        
    params['ctd']        = ctd        
    params['rounded_ctd']= rounded_ctd  
    params['daily_range']= daily_range
        
    num_zones = int(project.get('Zones', 'num_zones'))
    for zone in range (1, num_zones+1):        
        zone_section = 'Zone ' + str(zone)
        print(zone_section)
        
        num_ext_walls = project.getint(zone_section, 'num_ext_walls')

        #DOORS
        for ext_wall in range (1, num_ext_walls + 1):
            ext_wall_section    = zone_section + ' ExtWall ' + str(ext_wall)
            num_door_types      = project.getint(ext_wall_section, 'num_door_types')
            direction           = project.get(ext_wall_section, 'direction')                 #'N'
            params['direction'] = direction
            
            for door_type in range(1, num_door_types + 1):
                door_section         = ext_wall_section + ' Door ' + str(door_type)
                params['section']    = door_section
                params['panel_type'] = 'door'

                print(4*" " + door_section                            )
                
                door_results = get_opaque_panel(params)                 
                doors.append(door_results)
            #endfor
        #endfor
        params.pop('direction', None)  #get rid of the direction

        #WALLS
        for ext_wall in range (1, num_ext_walls + 1):
            ext_wall_section     = zone_section + ' ExtWall ' + str(ext_wall)            
            params['section']    = ext_wall_section
            params['panel_type'] = 'ext_wall'

            print(4*" " + ext_wall_section                        )
            
            ext_wall_results = get_opaque_panel(params) 
            
            if ext_wall_results['wall_type']   == 'above_grade':
                ag_walls.append(ext_wall_results)
            elif ext_wall_results['wall_type'] == 'partition':
                p_walls.append(ext_wall_results)
            elif ext_wall_results['wall_type'] == 'below_grade':
                bg_walls.append(ext_wall_results)
            else:
                print ("wall_type not defined")
                sys.exit()
            #endif
        #endfor

        num_ceilings = project.getint(zone_section, 'num_ceilings')
        for ceiling in range (1, num_ceilings + 1):
            ceiling_section = zone_section + ' Ceiling ' + str(ceiling)
            print( 4*" " + ceiling_section       )
            params['section']    = ceiling_section
            params['panel_type'] = 'ceiling'
            ceiling_results      = get_opaque_panel(params)                        
            ceilings.append(ceiling_results)
        #endfor
        
        num_p_ceilings = project.getint(zone_section, 'num_p_ceilings')
        for p_ceiling in range (1, num_p_ceilings + 1):
            p_ceiling_section = zone_section + ' PCeiling ' + str(p_ceiling)            
            print (4*" " + p_ceiling_section)
            params['section'] = p_ceiling_section
            params['panel_type'] = 'p_ceiling'
            p_ceiling_results = get_opaque_panel(params)            
            p_ceilings.append(p_ceiling_results)
        #endfor
        
        num_floors = int(project.get(zone_section, 'num_floors'))
        for floor in range (1, num_floors + 1):
            floor_section = zone_section + ' Floor ' + str(floor)            
            print (4*" " + floor_section)
            params['section'] = floor_section
            params['panel_type'] = 'floor'
            floor_results = get_opaque_panel(params)                        
            floors.append(floor_results)            
        #endfor

        num_p_floors = int(project.get(zone_section, 'num_p_floors'))
        for p_floor in range (1, num_p_floors + 1):
            p_floor_section = zone_section + ' PFloor ' + str(p_floor)            
            print( 4*" " + p_floor_section)
            params['section'] = p_floor_section
            params['panel_type'] = 'p_floor'
            p_floor_results = get_opaque_panel(params)            
            p_floors.append(p_floor_results)            
        #endfor
    #endfor 

    results = {
        'htd'        : htd,
        'ctd'        : ctd,
        'rounded_ctd': rounded_ctd,
        'daily_range': daily_range,
        'doors'      : doors,
        'ag_walls'   : ag_walls,
        'p_walls'    : p_walls,
        'bg_walls'   : bg_walls,
        'ceilings'   : ceilings,
        'p_ceilings' : p_ceilings,
        'floors'     : floors,
        'p_floors'   : p_floors
    }
    
    output_worksheet_d(results)
    
    return results
#enddef
