
#------------------------------------------------------------------------------
#   Worksheet F: Internal Loads
#------------------------------------------------------------------------------

def output_worksheet_f(results):
    msg = ""
    msg = msg +  60 * "=" + "\n"
    msg = msg +  "Worksheet F: Internal Loads" + "\n"
    msg = msg +  60 * "-" + "\n"
    msg = msg + "     output not created yet (come check data)\n"
    msg = msg +  60 * "=" + "\n"
    print(msg)
    
#enddef


def worksheet_f(settings, project):

    #put something here to check if project.hasoption for num_occupants so can
    #override default if necessary
    num_occupants = project.getint('Internal', 'num_bedrooms') + 1
    occupant_sens_load = 230 * num_occupants
    occupant_lat_load  = 200 * num_occupants

    default_sens_load  = project.getfloat('Internal', 'appliance_load')

    plant_lat_load  = 0
    p1 = 10 * project.getint('Internal', 'num_small_plants')
    p2 = 20 * project.getint('Internal', 'num_medium_plants')
    p3 = 30 * project.getint('Internal', 'num_large_plants')
    plant_lat_load = p1 + p2 + p3
    
    results = {
        'occupant_sens_load'  : occupant_sens_load,
        'occupant_lat_load'   : occupant_lat_load,
        'default_sens_load'   : default_sens_load,
        'default_lat_load'    : 0,
        'adjust_sens_load'    : 0,
        'adjust_lat_load'     : 0,
        'appliance_sens_load' : 0,
        'appliance_lat_load'  : 0,
        'plant_sens_load'     : 0,
        'plant_lat_load'      : plant_lat_load,
    }
    
    output_worksheet_f(results)
    
    return results
#enddef

