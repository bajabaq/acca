
import os
import configparser




def site_survey2():
    #this function will gather all of the site information so that man-j (or man-jae) can be calculated
    print("Enter Project Street Address"
    address = "1070 Kismet Dr."    
    print(address
    print("Enter City"
    city = "Aiken"
    print(city
    print("Enter State"
    state = "SC"
    print(state
        
    address = address + ", " + city + ", " + state
    
    #address = "1741 Huckleberry Dr., Aiken, SC"
    #address = "802 Arcadia Lakes Dr., Columbia, SC"
    address = "Vallero Residence, Houston, TX"
    
    #use project address, city, and state to get design city, state - store that in the project file
    
    outdoor_design_conditions = get_table1_data(address)
    
    indoor_design_conditions  = get_indoor_design(address)
    
    print("Enter the Number of Zones (or floors)"
    zone = 1
    print(zone
    
    
    location_info = (address, outdoor_design_conditions, indoor_design_conditions)
    return location_info
#enddef

def site_survey():
    print("\tDoing site_survey"
        
    project = configparser.Safeconfigparser()
    
    project_file = os.path.abspath('projects/vatilo_residence.txt')      
    project.read(project_file)
        
    project_name = project.get('Location', 'project_name')            
    print("\tSite survey complete for " + project_name
    
    return project
#enddef

if __name__ == '__main__':
    print("doing this standalone"
    
    #for Manual T - will need to know if this is new construction or a system retrofit
    #   because will need to know where supply/return air terminals are located 
    #   or will need to know to provide estimates of "best location" for those terminals
    #   so can report these are all your options or these are your options with what you have now
    
#endif