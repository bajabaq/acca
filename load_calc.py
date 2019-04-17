import os
import sys
import math
import configparser

from hvac_database import get_db_filename, do_query
from hvac_math     import interpolate_val

from load_calc_wksht_a import worksheet_a
from load_calc_wksht_b import worksheet_b
from load_calc_wksht_c import worksheet_c
from load_calc_wksht_d import worksheet_d
from load_calc_wksht_e import worksheet_e
from load_calc_wksht_f import worksheet_f
from load_calc_wksht_g import worksheet_g
from load_calc_wksht_h import worksheet_h

from load_calc_j1      import form_j1ae, form_j1

def calc_condensation(address, heating_dry_bulb_temp):
    #may need structural information before can actually do this!!
    #calculate if there would be visible condenstion
    #calculate if there would be concealed condenstion
    #AND together - if 1 then 
    #see section 27 of manual p 219
    condensation = False
    return condensation
#enddef


def create_points():    
    print("Enter Project Street Address")
    address = "1070 Kismet Dr."
    #address = "1741 Huckleberry Dr."
    #address = "802 Arcadia Lakes Dr."
    print(address)
    print("Enter City")
    city = "Aiken"
    print(city)
    print("Enter State")
    state = "SC"
    print(state)
    #link in w/ Google Maps and clickable outline of building to create points
    
    address = address + " " + city + ", " + state
    
    print("Finding nearest comparible location...")
    #create sub here"
    city  = "Augusta"
    state = "GA"    
    print("Using " + city + ", " + state + " for design conditions")
    #return city, state from sub
    
    location = (address, city, state)
    
    return location
#enddef


def read_points(location):
    address = location[0]
    
    #points created in http://itouchmap.com/latlong.html
    if ('kismet' in address.lower()):        
        points = ((33.513124, -81.742963),  #top-left - going clockwise
                  (33.513091, -81.742852),
                  (33.512868, -81.742938),
                  (33.512898, -81.743049))
    elif('huckleberry' in address.lower()):
        points = ((33.515259, -81.759828),  #top-left - going clockwise
                  (33.515227, -81.759685),
                  (33.515007, -81.759752),
                  (33.515036, -81.759893))
    elif('arcadia' in address.lower()):
        points = ((34.054096, -80.960623), #top-left - going clockwise
                  (34.054028, -80.960487),
                  (34.053974, -80.960529),
                  (34.054043, -80.960661))                  
    else:
        print("ERROR - location not found, come add points")
        sys.exit()
    #endif
    return points
#enddef


#see here: http://gis.stackexchange.com/questions/29239/calculate-bearing-between-two-decimal-gps-coordinates
#check via http://www.geomidpoint.com/destination/
def calc_headings(points):
    headings = []
    last_point = len(points)-1
    for i in range(0, last_point+1):        
        if i == last_point:
            lat1 = points[i][0]
            lng1 = points[i][1]
            lat2 = points[0][0]
            lng2 = points[0][1]
        else:
            lat1 = points[i][0]
            lng1 = points[i][1]
            lat2 = points[i+1][0]
            lng2 = points[i+1][1]
        #endif
        #print(lat1, lng1, lat2, lng2  )      
        startLat  = math.radians(lat1)
        startLong = math.radians(lng1)
        endLat    = math.radians(lat2)
        endLong   = math.radians(lng2)

        dLong = endLong - startLong
        dPhi  = math.log(math.tan(endLat/2.0+math.pi/4.0)/math.tan(startLat/2.0+math.pi/4.0))

        if abs(dLong) > math.pi:
             if dLong > 0.0:
                 dLong = -(2.0 * math.pi - dLong)
             else:
                 dLong = (2.0 * math.pi + dLong)

        bearing = (math.degrees(math.atan2(dLong, dPhi)) + 360.0) % 360.0;
        #print(bearing)
        
        headings.append(bearing)
    #endfor
    
    return headings
#enddef    

        
#calc 90degrees to heading (which way exposed)
#take heading and add 90degrees
def calc_exposures(headings):    
    exposures = []
    for heading in headings:        
        exposure = (heading - 90) % 360        
        print("heading is " + str(heading) + " so exposure is " + str(exposure))
        exposures.append(exposure)
    #endfor

    return exposures
#enddef

#calc exposure label (N,NE,E,SE,S,SW,W,NW)
def calc_exposure_label(exposure):
    exposure_label = ''
    if(       0 <= exposure and exposure < 22.5):
        exposure_label = 'N'
    elif(  22.5 <= exposure and exposure < 45.0):
        exposure_label = 'NE'
    elif(  45.0 <= exposure and exposure < 67.5):
        exposure_label = 'NE'
    elif(  67.5 <= exposure and exposure < 90.0):
        exposure_label = 'E'
    elif(  90.0 <= exposure and exposure < 112.5):
        exposure_label = 'E'
    elif( 112.5 <= exposure and exposure < 135.0):
        exposure_label = 'SE'
    elif( 135.0 <= exposure and exposure < 157.5):
        exposure_label = 'SE'
    elif( 157.5 <= exposure and exposure < 180.0):
        exposure_label = 'S'
    elif( 180.0 <= exposure and exposure < 202.5):
        exposure_label = 'S'    
    elif( 202.5 <= exposure and exposure < 225.0):
        exposure_label = 'SW'
    elif( 225.0 <= exposure and exposure < 247.5):
        exposure_label = 'SW'    
    elif( 247.5 <= exposure and exposure < 270.0):
        exposure_label = 'W'
    elif( 270.0 <= exposure and exposure < 292.5):
        exposure_label = 'W'    
    elif( 292.5 <= exposure and exposure < 315.0):
        exposure_label = 'NW'
    elif( 315.0 <= exposure and exposure < 337.5):
        exposure_label = 'NW'    
    elif( 337.5 <= exposure and exposure < 360.0):
        exposure_label = 'N'
    #endif

    return exposure_label
#endfunc

def get_blower_heat_gain(project):
    result = 0
    if (project.get('Location','blower_heat_discount') == 'no'):
        result = 1707
    #endif
    
    return result
#enddef

#-------------------------------------------------------------
#   MAIN PROGRAM HERE
#-------------------------------------------------------------
def load_calc(project):
    
    #validate_project(project) #make sure project has all information required to do calcs

    #read the system settings file (maybe should be in own module - along w/ get_database name)
    settings      = configparser.ConfigParser()
    settings_file = os.path.abspath('system_settings.txt')    
    settings.read(settings_file)

    project_name = project.get('Location', 'project_name')
    print("\tDoing load calc (manual J or J-AE) for " + project_name)

    a_results = worksheet_a(settings, project)            #indoor and outdoor design conditions    
    b_results = worksheet_b(settings, project, a_results) #heating and cooling HTM and Load Area for Windows and Glass Doors
    c_results = worksheet_c(settings, project, a_results) #skylights
    d_results = worksheet_d(settings, project, a_results) #opaque panels
    e_results = worksheet_e(settings, project, a_results) #infiltration
    f_results = worksheet_f(settings, project)            #internal loads
    g_results = worksheet_g(settings, project, a_results) #duct runs in unconditioned spaces
    h_results = worksheet_h(settings, project, a_results) #engineered ventilation
    bhg_results = get_blower_heat_gain(project)
    
    worksheet_results = {'a' : a_results,
                         'b' : b_results,
                         'c' : c_results,
                         'd' : d_results,
                         'e' : e_results,                         
                         'f' : f_results,                         
                         'g' : g_results,
                         'h' : h_results,
                         'bhg': bhg_results}    
    
    form_j1ae(worksheet_results)
    
    #form_j1(worksheet_results)
    
#enddef


#-------------------------------------------------------------
#   STANDALONE HERE 
#-------------------------------------------------------------
if __name__ == '__main__':
    print("doing this standalone")
    
    project = configparser.ConfigParser()
    #project_file = os.path.abspath('projects/man_j_sec7/man_j_sec7.txt') #vatilo residence - block load
    #project_file = os.path.abspath('projects/man_j_sec8/man_j_sec8.txt') #victor residence - block load
    project_file = os.path.abspath('projects/29803_1741_huckleberry_dr/29803_1741_huckleberry_dr_up.txt') #whiteside residence - block load
    #project_file = os.path.abspath('projects/29803_1741_huckleberry_dr/29803_1741_huckleberry_dr_down.txt') #whiteside residence - block load
    project.read(project_file)
    
    load_calc(project)
    
    
    sys.exit()


    location  = create_points()


    points    = read_points(location)
    headings  = calc_headings(points)
    exposures = calc_exposures(headings)
    for exposure in (exposures):
        exposure_label = calc_exposure_label(exposure)
        print(exposure_label)
    #endfor


#endif
