#!/usr/bin/python

import os
import re
import ConfigParser

import curses

settings = './system_settings.txt'

def get_param(screen, default, prompt_string):
    screen.clear()
    screen.border(0)
    screen.addstr(2, 2, prompt_string + " [" + str(default) + "]")
    screen.refresh()
    xinput = screen.getstr(10, 10, 60)
    if xinput == '':
        xinput = default
    #endif
    return xinput
#enddef

def get_param_from_opts(screen, opts, prompt_string):
    repeat = True
    while repeat == True:
        repeat = False

        screen.clear()
        screen.border(0)
        screen.addstr(2, 2, prompt_string)
        i = 0
        for opt in opts:
            screen.addstr(i + 4, 4, str(i) + " - " + opt )
            i = i + 1
        #endfor   
        screen.addstr(i + 4, 4,'')
        screen.refresh()
        inp = screen.getstr()
    
        if inp == 'Q' or inp == 'q':
            return ''
        if inp.isdigit() and 0 <= int(inp) and int(inp) < len(opts):
            opt = opts[int(inp)]
        else:
            repeat = True
        #endif
    #endwhile
    return opt
#enddef


#TODO I DONT THINK THIS WORKS...
def get_yes_no(xinput):
    clean_input = xinput.lower()
    clean_input = clean_input[0][0]
    if clean_input == 'y':
        clean_input = 'yes'
    elif clean_input == 'n':
        clean_input = 'no'
    #endif
    return clean_input
#enddef



def get_valid_param(screen, config, sec, opt, default, user_instruction):
    repeat = True
    while repeat == True:
        val = get_param(screen, default, user_instruction)
        if isinstance(default, (int,long)):
            try:
                val = int(val)
                repeat = False
            except:
                repeat = True
        if isinstance(default, float):
            try:
                val = float(val)
                repeat = False
            except:
                repeat = True
        if isinstance(default, str):
            try:
                val = str(val)
                repeat = False
            except:
                repeat = True
    #endwhile
    config.set(sec, opt, str(val))
    return val
#enddef



#=================================================================================
# Configuration Input Information
#=================================================================================
def get_location_info(screen, config):
    sec    = 'Location'

    project_street_address = get_param(screen,'1 Main St'     , "Enter the Project's Street Address")
    project_city           = get_param(screen,'Aiken'         , "Enter the Project's City")
    project_state          = get_param(screen,'South Carolina', "Enter the Project's State")
    project_zip            = get_param(screen,'29803'         , "Enter the Project's Zip")

    config.add_section(sec)

    config.set(sec,'project_street_address', project_street_address)
    config.set(sec,'project_city'          , project_city)
    config.set(sec,'project_state'         , project_state)
    config.set(sec,'project_zip'           , project_zip)

    #TODO: use above information to find design city, state
    design_city  = get_param(screen,'Busytown', "Enter the Design City")
    design_state = get_param(screen,'State', "Enter the Design State")
    config.set(sec,'design_city', design_city)
    config.set(sec,'design_state', design_state)

    #TODO: does this belong here???
#    blower_heat_discount = ''
#    while (blower_heat_discount != 'yes' or blower_heat_discount != 'no'): 
#        blower_heat_discount = get_param(screen,'no', "Does this project get a discount for blower heat")
#        blower_heat_discount = get_yes_no(blower_heat_discount)
#    #endwhile
#    config.set(sec,'blower_heat_discount', blower_heat_discount)

    write_to_file(pfile,config)

    return pfile
#enddef

def get_num_systems(screen, config):
    sec       = 'Systems'
    opt1      = 'num_systems'
    num_zones = 1
    dopt1     = num_systems

    if config.has_section(sec) == False:
        config.add_section(sec)
    else:
        if config.has_option(opt1):
            default = config.get(sec, opt1)
        #endif
    #endif

    num_systems = get_valid_param(screen, config, sec, opt1, dopt1, "Enter Number of Systems")
    return num_systems
#enddef


def get_num_zones(screen, config):
    sec       = 'Zones'
    opt1      = 'num_zones'
    num_zones = 1
    dopt1     = num_zones

    if config.has_section(sec) == False:
        config.add_section(sec)
    else:
        if config.has_option(opt1):
            default = config.get(sec, opt1)
        #endif
    #endif

    num_zones = get_valid_param(screen, config, sec, opt1, dopt1, "Enter Number of Zones")
    return num_zones
#enddef

def get_zone_info(screen, config, zone):
    sec    = 'Zone ' + str(zone)
    opt1   = 'num_ext_walls'
    opt2   = 'num_ceilings'
    opt3   = 'num_p_ceilings'
    opt4   = 'num_floors'
    opt5   = 'floors_heated'
    opt6   = 'floors_cooled'
    opt7   = 'num_p_floors'
    opt8   = 'p_floors_heated'
    opt9   = 'p_floors_cooled'
    opt10  = 'num_ducts'

    dopt1  = 3
    dopt2  = 1
    dopt3  = 0
    dopt4  = 1
    dopt5  = 0
    dopt6  = 0
    dopt7  = 0
    dopt8  = 0
    dopt9  = 0
    dopt10 = 1

    if config.has_section(sec) == False:
        config.add_section(sec)
    else:
        if config.has_option(opt1):
            dopt1 = config.get(sec, opt1)
        if config.has_option(opt2):
            dopt2 = config.get(sec, opt2)
        if config.has_option(opt3):
            dopt3 = config.get(sec, opt3)
        if config.has_option(opt4):
            dopt4 = config.get(sec, opt4)
        if config.has_option(opt5):
            dopt5 = config.get(sec, opt5)
        if config.has_option(opt6):
            dopt6 = config.get(sec, opt6)
        if config.has_option(opt7):
            dopt7 = config.get(sec, opt7)
        if config.has_option(opt8):
            dopt8 = config.get(sec, opt8)
        if config.has_option(opt9):
            dopt9 = config.get(sec, opt9)
        if config.has_option(opt10):
            dopt10 = config.get(sec, opt10)
    #endif

    num_ext_walls = 0
    while num_ext_walls < 3:
        num_ext_walls = get_valid_param(screen, config, sec, opt1, dopt1, "Enter Number of Exterior Walls")
    #endwhile

    num_ceilings = 0
    while num_ceilings < 1:
        num_ceilings = get_valid_param(screen, config, sec, opt2, dopt2, "Enter Number of Ceilings (non-partition)")
    #endwhile

    get_valid_param(screen, config, sec, opt3, dopt3, "Enter Number of Partition Ceilings")

    num_floors = 0
    while num_floors < 1:
        num_floors = get_valid_param(screen, config, sec, opt4, dopt4, "Enter Number of Floors (non-partition)")
    #endwhile
    get_valid_param(screen, config, sec, opt5, dopt5, "Enter Number of these Floors that are Heated")
    get_valid_param(screen, config, sec, opt6, dopt6, "Enter Number of these Floors that are Cooled")

    num_p_floors = get_valid_param(screen, config, sec, opt7, dopt7, "Enter Number of Partition Floors")
    if num_p_floors > 0:
        get_valid_param(screen, config, sec, opt8, dopt8, "Enter Number of these P. Floors that are Heated")
        get_valid_param(screen, config, sec, opt9, dopt9, "Enter Number of these P. Floors that are Cooled")
    #endif

    num_ducts = 0
    while num_ducts < 1:
        num_ducts = get_valid_param(screen, config, sec, opt10, dopt10, "Enter Number of Duct Systems in Zone")
    #endwhile

    #heated/cooled (p)_floors should probably be a comma seperated list 

    for m1floor in range(num_floors):
        floor = m1floor + 1
        get_floor_info(screen, config, zone, floor)
    #endfor

    #what about p_floor_info?

    for m1ceiling in range(num_ceilings):
        ceiling = m1ceiling + 1
        get_ceiling_info(screen, config, zone, ceiling)
    #endfor

    #what about p_ceiling_info

    for m1extwall in range(num_ext_walls):
        extwall = m1extwall + 1
        get_ext_wall_info(screen, config, zone, extwall)
    #endfor

    for m1ducts in range(num_ducts):
        duct = m1ducts + 1
        get_duct_info(screen, config, zone, duct)
    #endfor

#enddef

def get_internal_info(screen, config):
    sec    = 'Internal'
    opt1   = 'num_bedrooms'
    opt2   = 'num_occupants'
    opt3   = 'num_small_plants'
    opt4   = 'num_medium_plants'
    opt5   = 'num_large_plants'

    num_bedrooms     = 1
    num_occupants    = num_bedrooms + 1
    num_small_plants = 0
    num_medium_plants= 0
    num_large_plants = 0

    dopt1 = num_bedrooms
    dopt2 = num_occupants
    dopt3 = num_small_plants
    dopt4 = num_medium_plants
    dopt5 = num_large_plants

    if config.has_section(sec) == False:
        config.add_section(sec)
    else:
        if config.has_option(opt1):
            dopt1 = config.get(sec, opt1)
        if config.has_option(opt2):
            dopt2 = config.get(sec, opt2)
        if config.has_option(opt3):
            dopt3 = config.get(sec, opt3)
        if config.has_option(opt4):
            dopt4 = config.get(sec, opt4)
        if config.has_option(opt5):
            dopt5 = config.get(sec, opt5)
    #endif

    num_bedrooms = get_valid_param(screen, config, sec, opt1, dopt1,  "Enter Number of Bedrooms")
    dopt2 = num_bedrooms + 1
    get_valid_param(screen, config, sec, opt2, dopt2,  "Enter Number of Occupants")
    get_valid_param(screen, config, sec, opt3, dopt3,  "Enter Number of Small Plants")
    get_valid_param(screen, config, sec, opt4, dopt4,  "Enter Number of Medium Plants")
    get_valid_param(screen, config, sec, opt5, dopt5,  "Enter Number of Large Plants")
#enddef


def get_floor_info(screen, config, zone, floor):
    sec    = 'Zone ' + str(zone) + ' Floor ' + str(floor)
    config.add_section(sec)

    length = 0
    while length < 1:
        length = get_param(screen, 1, "Enter Floor Length (ft)")
    #endwhile
    config.set(sec, 'length', length)

    width = 0
    while width < 1:
        width = get_param(screen, 1, "Enter Floor Width (ft)")
    #endwhile
    config.set(sec, 'width', width)

    insulation = 0
    while insulation < 0:
        insulation = get_param(screen, 0, "Enter Floor Insulation R-value")
    #endwhile
    config.set(sec, 'insulation', insulation)

    #like maybe for a trap door to a wine celler?
    area_of_openings = 0
    while area_of_openings < 0:
        area_of_openings = get_param(screen, 0, "Enter Area of Openings in Floor (sq ft)")
    #endwhile
    config.set(sec, 'area_of_openings', area_of_openings)

    floor_type = get_param(screen, 'floor', "Enter Floor Type")
    config.set(sec, 'floor_type', floor_type)

    construction_number = get_param(screen, '22A', "Enter Floor Type Construction Number")
    config.set(sec, 'construction_number', construction_number)

    floor_construction_code = get_param(screen, 'p', "Enter Floor Construction Code")
    config.set(sec, 'construction_number', floor_construction_code)

    soil_condition_code = get_param(screen, 'h', "Enter Soil Condition Code")
    config.set(sec, 'soil_condition_code', soil_condition_code)

    write_to_file(pfile, config)
#enddef


def get_ceiling_info(screen, config, zone, ceiling):
    sec    = 'Zone ' + str(zone) + ' Ceiling ' + str(ceiling)
    config.add_section(sec)

    length = 0
    while length < 1:
        length = get_param(screen, 1, "Enter Ceiling Length (ft)")
    #endwhile
    config.set(sec, 'length', length)

    width = 0
    while width < 1:
        width = get_param(screen, 1, "Enter Ceiling Width (ft)")
    #endwhile
    config.set(sec, 'width', width)

    slope = 0
    while slope < 0:
        slope = get_param(screen, 0, "Enter Ceiling Slope (UNITS?)")
    #endwhile
    config.set(sec, 'slope', slope)

    insulation = 0
    while insulation < 0:
        insulation = get_param(screen, 0, "Enter Ceiling Insulation R-value")
    #endwhile
    config.set(sec, 'insulation', insulation)

    num_skylight_types = 0
    while num_skylight_types < 0:
        num_skylight_types = get_param(screen, 0, "Number of Types of Skylights")
    #endwhile
    config.set(sec, 'num_skylight_types', num_skylight_types)

    #if num_skylight_types > 0: #go off and get skylight info then return and do rest

    #maybe calculate from worksheetC skylights...
    area_of_openings = 0
    while area_of_openings < 0:
        area_of_openings = get_param(screen, 0, "Enter Area of Openings in Floor (sq ft)")
    #endwhile
    config.set(sec, 'area_of_openings', area_of_openings)


    construction_number = get_param(screen, '16B', "Enter Ceiling Type Construction Number")
    config.set(sec, 'construction_number', construction_number)

    roof_material_code = get_param(screen, 'a', "Enter Roof Material Code")
    config.set(sec, 'roof_material_code', roof_material_code)

    roof_color = get_param(screen, 'd', "Enter Roof Color Code")
    config.set(sec, 'roof_color', roof_color)

    write_to_file(pfile, config)
#enddef


def get_ext_wall_info(screen, config, zone, extwall):
    sec    = 'Zone ' + str(zone) + ' ExtWall ' + str(extwall)
    config.add_section(sec)

    direction = get_param(screen, 'N', "Enter Ext Wall Direction (N/S/E/W)")
    config.set(sec, 'direction', direction)

    length = 0
    while length < 1:
        length = get_param(screen, 1, "Enter Ext Wall Length (ft)")
    #endwhile
    config.set(sec, 'length', length)

    width = 0
    while width < 1:
        width = get_param(screen, 1, "Enter Ext Wall Width (ft)")
    #endwhile
    config.set(sec, 'width', width)

    height = 0
    while height < 0:
        height = get_param(screen, 0, "Enter Ext Wall Height (ft)")
    #endwhile
    config.set(sec, 'height', height)

    board_insulation = 0
    while board_insulation < 0:
        board_insulation = get_param(screen, 0, "Enter Ext Wall Insulation R-value")
    #endwhile
    config.set(sec, 'board_insulation', board_insulation)

    wall_type = get_param(screen, 'above_grade', "Enter Ext Wall Type")
    config.set(sec, 'wall_type', wall_type)

    construction_number = get_param(screen, '12C', "Enter Ext Wall Construction Number")
    config.set(sec, 'construction_number', construction_number)

    exterior_material = get_param(screen, 's', "Enter Ext Wall Exterior Material")
    config.set(sec, 'exterior_material', exterior_material)

    framing_material = get_param(screen, 'w', "Enter Ext Wall Framing Material")
    config.set(sec, 'framing_material', framing_material)

    windows_area     = 0
    num_window_types = 0
    while num_window_types < 0:
        num_window_types = get_param(screen, 0, "Number of Types of Windows")
    #endwhile
    config.set(sec, 'num_window_types', num_window_types)
    if num_window_types > 0:  #go off and get window info then return and do rest
        for m1window_type in range(num_window_types):
            window_type = m1window_type + 1
            get_window_type_info(screen, config, sec, window_type, window_area)
            windows_area = windows_area + window_area
        #endfor
    #endif

    doors_area     = 0
    num_door_types = 0
    while num_door_types < 0:
        num_door_types = get_param(screen, 0, "Number of Types of Doors")
    #endwhile
    config.set(sec, 'num_door_types', num_door_types)
    if num_door_types > 0:  #go off and get door info then return and do rest
        for m1door_type in range(num_door_types):
            door_type = m1door_type + 1
            get_door_type_info(screen, config, sec, door_type, door_area)
            doors_area = doors_area + door_area
        #endfor
    #endif

    #maybe calculate from worksheetB and doors...
    area_of_openings = -1
    while area_of_openings < 0:
        area_of_openings = windows_area + doors_area
        area_of_openings = get_param(screen, area_of_openings, "Enter Area of Openings in Ext Wall(sq ft)")
    #endwhile
    config.set(sec, 'area_of_openings', area_of_openings)

    write_to_file(pfile, config)
#enddef


def get_window_type_info(screen, config, sec, window_type, window_area):
    sec    = sec + ' Window ' + str(window_type)
    config.add_section(sec)

    num_of_type = 0
    while num_of_type < 1:
        num_of_type = get_param(screen, 1, "Enter Number of Windows of This type in This Wall (Including Sliding Glass Doors)")
    #endwhile
    config.set(sec, 'num_of_type', num_of_type)

    width = 0
    while width < 1:
        width = get_param(screen, 1, "Enter Window Width (ft)")
    #endwhile
    config.set(sec, 'width', width)

    height = 0
    while height < 0:
        height = get_param(screen, 0, "Enter Window Height (ft)")
    #endwhile
    config.set(sec, 'height', height)

    window_area = width * height * num_of_type

    num_panes_thick = 0
    while num_panes_thick < 1:
        num_panes_thick = get_param(screen, 2, "Enter Number of Window Panes Thick")    #endwhile
    config.set(sec, 'num_panes_thick', num_panes_thick)

    frame_type = get_param(screen, 'mb', "Enter Window Frame Type")
    config.set(sec, 'frame_type', frame_type)
    
    construction_number = get_param(screen, '1D-c', "Enter Window Construction Number")
    config.set(sec, 'construction_number', construction_number)

    insect_screen = get_param(screen, 'full indoor', "Enter Window Screen Type")
    config.set(sec, 'insect_screen', insect_screen)

    internal_shade = get_param(screen, 'blinds', "Enter Internal Window Shade")
    config.set(sec, 'insect_screen', internal_shade)
    
    overhang_width = 0
    while overhang_width < 0:
        overhang_width = get_param(screen, 1, "Width of Roof Overhang (ft)")
    #endwhile
    config.set(sec, 'overhang_width', overhang_width)

    height_to_overhang = 0
    while height_to_overhang < 0:
        height_to_overhang = get_param(screen, 1, "Distance from top of window to Roof Overhang (ft)")
    #endwhile
    config.set(sec, 'height_to_overhang', height_to_overhang)

    window_door_type = get_param(screen,'default', "Type of Window (or Door)")
    config.set(sec,'window_door_type', window_door_type)
#enddef


def get_door_type_info(screen, config, sec, door_type, door_area):
    sec    = sec + ' Door ' + str(door_type)
    config.add_section(sec)

    construction_number = get_param(screen, '11N', "Enter Door Construction Number")
    config.set(sec, 'construction_number', construction_number)

    #TODO change this to 'width' but 'length' is what looking for in wksht_XX code
    length = 0
    while length < 1:
        length = get_param(screen, 1, "Enter Door Width (ft)")
    #endwhile
    config.set(sec, 'length', length)

    height = 0
    while height < 0:
        height = get_param(screen, 0, "Enter Door Height (ft)")
    #endwhile
    config.set(sec, 'height', height)

    door_area = length * height

    percent_area_glass = 0
    while percent_area_glass < 0:
        percent_area_glass = get_param(screen, 0, "Enter Percent Area of Door that is Glass (%)")
    #endwhile
    config.set(sec, 'percent_area_glass', percent_area_glass)

#enddef



def get_duct_pipe_info(screen, config, sec, pipe_type, pipe_num):
    sec = sec + ' ' + pipe_type + ' ' + str(pipe_num)
    config.add_section(sec)

    diameter = -1
    while diameter < 0:
        diameter = get_param(screen, 1, "Diameter Duct " + pipe_type + ' ' + str(pipe_num))
    #endwhile
    config.set(sec, 'diameter', diameter)

    length = -1
    while length < 0:
        length = get_param(screen, 1, "Length Duct " + pipe_type + ' ' + str(pipe_num))
    #endwhile
    config.set(sec, 'length', length)

#enddef



def get_duct_info(screen, config, zone, duct):
    sec    = 'Zone ' + str(zone) + ' Duct ' + str(duct)
    config.add_section(sec)

    construction_number = get_param(screen, '7A-AE', "Enter Duct Construction Number")
    config.set(sec, 'construction_number', construction_number)

    #these are defaults - improved is 0.12/0.24, higher has to be done by field test
    rval = get_param(screen, 4, "Duct Insulation R-Value")
    config.set(sec, 'r-val', rval)

    leakage_supply = get_param(screen, 0.35, "Duct Leakage - Supply")
    config.set(sec, 'leakage_supply', leakage_supply)

    leakage_return = get_param(screen, 0.70, "Duct Leakage - Return")
    config.set(sec, 'leakage_return', leakage_return)

    improved_rval = get_param(screen, 8, "Improved Duct Insulation R-Value")
    config.set(sec, 'improved_r-val', improved_rval)

    improved_leakage_supply = get_param(screen, 0.12, "Improved Duct Leakage - Supply")
    config.set(sec, 'improved_leakage_supply', improved_leakage_supply)

    improved_leakage_return = get_param(screen, 0.24, "Improved Duct Leakage - Return")
    config.set(sec, 'improved_leakage_return', improved_leakage_return)

    num_supply_branches = 0
    while num_supply_branches < 0:
        num_supply_branches = get_param(screen, 10, "Number Duct Supply Branches")
    #endwhile
    config.set(sec, 'num_supply_branches', num_supply_branches)

    for m1supply_branch in range(num_supply_branches):
        supply_branch = m1supply_branch + 1
        get_duct_pipe_info(screen, config, sec, 'Supply Branch', supply_branch)
    #endfor

    num_return_trunks = 0
    while num_return_trunks < 0:
        num_return_trunks = get_param(screen, 1, "Number Duct Return Trunks")
    #endwhile
    config.set(sec, 'num_return_trunks', num_return_trunks)

    for m1return_trunk in range(num_return_trunks):
        return_trunk = m1return_trunk + 1
        get_duct_pipe_info(screen, config, sec, 'Return Trunk', return_trunk)
    #endfor

    write_to_file(pfile, config)
#enddef



#-----------------------------------------------------------------------------
# Real work done here
# work_type = 'new', 'edit', 'check'
#-----------------------------------------------------------------------------
def do_jabr(screen, pfile, work_type):
    if work_type == 'check' or work_type == 'edit':  #not done yet
        xinput = get_param(screen, '', "Work_Type " + work_type + " not done yet")
        return

    config = ConfigParser.SafeConfigParser()
    config.read(pfile)

	num_systems = get_num_systems(screen, config)
    num_zones = get_num_zones(screen, config)
    for m1zone in range(num_zones):
        zone = m1zone + 1
        get_zone_info(screen, config, zone)
    #endfor

    #TODO should internal be for each zone?? probably
    get_internal_info(screen, config)


    write_to_file(pfile,config)
#enddef

def do_jfull(screen, pfile, work_type):
    if work_type == 'check':  #not done yet
        xinput = get_param(screen, '', "Work_Type " + work_type + " not done yet")
        return

    config = ConfigParser.SafeConfigParser()
    config.read(pfile)

    write_to_file(pfile,config)
#enddef

def do_d(screen, pfile, work_type):
    if work_type == 'check':  #not done yet
        xinput = get_param(screen, '', "Work_Type " + work_type + " not done yet")
        return

    config = ConfigParser.SafeConfigParser()
    config.read(pfile)

    write_to_file(pfile,config)
#enddef

def do_s(screen, pfile, work_type):
    if work_type == 'check':  #not done yet
        xinput = get_param(screen, '', "Work_Type " + work_type + " not done yet")
        return

    config = ConfigParser.SafeConfigParser()
    config.read(pfile)

    write_to_file(pfile,config)
#enddef

def do_t(screen, pfile, work_type):
    if work_type == 'check':  #not done yet
        xinput = get_param(screen, '', "Work_Type " + work_type + " not done yet")
        return

    config = ConfigParser.SafeConfigParser()
    config.read(pfile)

    write_to_file(pfile,config)
#enddef


#-----------------------------------------------------------------------------
# write out the configuration to the pfile
#-----------------------------------------------------------------------------
def write_to_file(pfile,config):
    with open(pfile,'w+') as configfile:
        config.write(configfile)
    #endwith    
#enddef

#-----------------------------------------------------------------------------
# Dispatching done here
# work_type = 'new', 'edit', 'check'
# pfile is project file
# calc_type is J-full, J-abr, D, S, T
#-----------------------------------------------------------------------------
def work_on_project(screen, work_type, pfile, calc_type):
    if calc_type == 'J-abr':
        do_jabr(screen, pfile, work_type)
    elif calc_type == 'J-full':
        do_jfull(screen, pfile, work_type)
    elif calc_type == 'D':
        do_d(screen, pfile,work_type)
    elif calc_type == 'S':
        do_s(screen, pfile,work_type)
    elif calc_type == 'T':
        do_t(screen, pfile,work_type)
    #endif
#enddef


#=============================================================================
# GET THE PROJECT FILES
#=============================================================================
#-----------------------------------------------------------------------------
# make the project file
#-----------------------------------------------------------------------------
def make_pfile(screen):
    xisfile = True
    while xisfile == True:
        project_street_address = get_param(screen,'1 Main St'     , "Enter the Project's Street Address")
        project_city           = get_param(screen,'Aiken'         , "Enter the Project's City")
        project_state          = get_param(screen,'South Carolina', "Enter the Project's State")
        project_zip            = get_param(screen,'29803'         , "Enter the Project's Zip")

        pfile = str(project_zip) + '_' + str(project_street_address)
        pfile = pfile.lower()
        pfile = re.sub(r' ','_',pfile)
        pfile = re.sub(r'\W+','',pfile)

        pdir  = './projects/' + pfile

        pfile = pdir + '/' + pfile + '.txt'

        if os.path.isfile(pfile) == True:
            screen.clear()
            screen.border(0)
            screen.addstr(2, 2, "File " + pfile + " Exists - cannot make")
            screen.addstr(4, 2, "Press Q to quit or C to continue")
            screen.refresh()
            xinput = screen.getstr(10, 10, 60)
            if xinput == 'Q' or xinput == 'q':
                return ''
            #endif
        else:
            xisfile = False
            if not os.path.isfile(pdir):
                os.makedirs(pdir)
        #endif
    #endwhile

    config = ConfigParser.RawConfigParser()
    sec = 'Location'
    config.add_section(sec)

    config.set(sec,'project_street_address', project_street_address)
    config.set(sec,'project_city'          , project_city)
    config.set(sec,'project_state'         , project_state)
    config.set(sec,'project_zip'           , project_zip)
    
    write_to_file(pfile, config)

    return pfile
#enddef

#-----------------------------------------------------------------------------
# Choose the project file or return empty string
#-----------------------------------------------------------------------------
def pick_pfile(screen):
    config = ConfigParser.SafeConfigParser()
    sfile  = config.read(settings)
    pdir   = './' + config.get('system','project_dir')

    #get the projects
    lprojects = []
    for dirname, dirnames, filenames in os.walk(pdir):
        dirnames.sort()
        for subdirname in dirnames:
            pname = os.path.join(dirname,subdirname,subdirname) + ".txt"
            lprojects.append(pname)
        #endfor
    #endfor

    #pick the project
    pfile = get_param_from_opts(screen, lprojects , "Enter the number to choose a Project (or Q to quit)")
    if pfile == 'Q' or pfile == 'q':
        pfile = ''
    #endif
    return pfile
#endef

#-----------------------------------------------------------------------------
# Types of ACCA calculations Manuals J-full, J-abr, D, S, T
#-----------------------------------------------------------------------------
def get_calc_type(screen):
    calc_types = ['J-full','J-abr','D','S','T']
    calc_type = get_param_from_opts(screen, calc_types , "Calculation Type (or Q to quit)")

    return calc_type
#enddef

#-----------------------------------------------------------------------------
# MAIN CODE HERE
#-----------------------------------------------------------------------------
def _main():
    x = 0
    while x != ord('4'):
        screen = curses.initscr()

        screen.clear()
        screen.border(0)
        screen.addstr(2, 2, "Please enter a number...")
        screen.addstr(4, 4, "1 - Create new project")
        screen.addstr(5, 4, "2 - Edit existing project")
        screen.addstr(6, 4, "3 - Check existing project")
        screen.addstr(7, 4, "4 - Exit")
        screen.refresh()

        x = screen.getch()

        if x == ord('4'):
            curses.endwin()
            os.system("clear")
            return
        #endif

        #get work type
        work_type = ''
        if x == ord('1'):
            work_type = 'new'
        elif x == ord('2'):
            work_type = 'edit'
        elif x == ord('3'):
            work_type = 'check'
        #endif

        #get the project file
        pfile = ''
        if x == ord('1'):
            pfile = make_pfile(screen)
        elif x == ord('2') or x == ord('3'):        
            pfile = pick_pfile(screen)
        #endif

        if pfile == '':
            x = 0
        else:
            calc_type = get_calc_type(screen)
            work_on_project(screen, work_type, pfile, calc_type)
        #endif
        curses.endwin()
    #endwhile
    os.system("clear")
#enddef

#-----------------------------------------------------------------------------

_main()

exit()
