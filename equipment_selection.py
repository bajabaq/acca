import os
import csv
import configparser

#---------------------------------------------------------------------
# do query
#---------------------------------------------------------------------
def do_query(equipment, query):
    csvData  = csv.reader(open(equipment))
    csvTable = []
    isHeader = True

    for row in csvData:
        if isHeader:
            isHeader = False
            headerRow = row
            for i in range(len(headerRow)):
                # replace spaces w/ underscores in column headers
                headerRow[i] = headerRow[i].replace(' ', '_')
            #endfor
        else:
            csvTable.append(row)
        #endif
    #endfor

    # determine column types: string/int/float
    colType = []
    j = 0
    for i in range(len(headerRow)):
        isFloat = False
        isInt   = False
        
        #detecting type is not working (all ints are floats --- maybe OK)
        for j in range(len(csvTable)):
            try:
                v = int(csvTable[j][i])                
                isInt   = True
                isFloat = False
            except ValueError:                
                pass
            try:
                v = float(csvTable[j][i])                
                isFloat = True
                isInt   = False
            except ValueError:
                pass       
        #endfor

        
        colT = ''
        if isInt:
            colT = 'int'
        elif isFloat:
            colT = 'float'
        else:
            colT = 'string'
        #endif
        
        
        colType.append(colT)

        print(headerRow[i], colT)
    #endfor
    
    
    
    # run the query
    matches = 0
    for j in range(len(csvTable)):
        # assign the column variables
        for i in range(len(headerRow)):
            if colType[i] == 'string':
                exec(headerRow[i] + '=' + '"' + csvTable[j][i] + '"')
            elif colType[i] == 'float':
                exec(headerRow[i] + '=' + 'float("' + csvTable[j][i] + '")')
            elif colType[i] == 'int':
                exec(headerRow[i] + '=' + 'int("' + csvTable[j][i] + '")')
            #endif
        #endfor
        
        # output the rows matching the query
        if eval(query):
            print(headerRow)
            print(csvTable[j])
            matches = matches + 1
        #endif
    #endfor
    print("Num matching system setups " + str(matches) + " out of " + str(j+1))
#enddef


#---------------------------------------------------------------------
# this function is based on Manual S Table 1-4 (more detail needed? LAT/Room DB?)
#---------------------------------------------------------------------
def get_td_value(shr):
    td = 0
    if (shr < 0.80):
        td = 21
    elif (shr > 0.85):
        td = 17
    else:
        td = 19
    #endif
    return td
#enddef


def equipment_selection(project):
    project_name = project.get('Location', 'project_name')        
    print("\tDoing manual S for " + project_name)
    
    print("\tCalculate approximate Cooling CFM:")
    
    sensible_load = project.getfloat('Design Parameters','sensible_load')
    latent_load   = project.getfloat('Design Parameters','latent_load')
    total_load    = sensible_load + latent_load
    print("\tTotal Load: " + str(total_load) + " BTUH")
    
    #determine if there is a ventilation load or a duct gain and then use
    #table 1-2 and 3-1 to create 
    #entering dry-bulb temp
    #entering wet-bulb temp
    
    #Future - water-to-air equipment adjustments
    
    shr = sensible_load / total_load #sensible heat ratio    
    print("\tSHR: " + str(shr))
    
    indoor_db = project.getfloat('Design Parameters','indoor_dry_bulb')    
    td = get_td_value(shr) 
    
    print("\tTD: " + str(td))
    
    cooling_cfm = sensible_load / (1.1 * td)
    print("\tCooling CFM: " + str(cooling_cfm))
    
    #search for equipment packages where:
    #equip_total_capacity >= design_total_capacity (not greater than 40% - what's the limit here?, difference is small as possible)
    #equip_nominal_cfm = cooling_cfm (+/- X%)
    
    max_equip_cap = total_load * 1.4
    print("\tMax Equipment Capacity: " + str(max_equip_cap))
    
    return
    
    query = 'total_cool_cap >= ' + str(total_load) + ' and total_air_flow > ' + str(cooling_cfm) + ' and total_cool_cap <= ' + str(max_equip_cap)
    
    print(query)
    
    #get equipment packages to query
    equipment_tables = ['equip_data\example_data.txt']
    for equipment in equipment_tables:
        print("do query on " + str(equipment))
        do_query(equipment, query)
    #endfor
    
        
    #see page 3-5 step 4
    
    #if equip_sensible_capacity >= design_sensible_load
    #   AND equip_latent_capacity >= design_latent_load
    #       then system is OK
    #   OR if equip_sensible_capacity < design_sensible_load
    #      BUT/AND equip_latent_capacity > design_latent_load
    #       then 
    #       total_equip_sens_capacity = equip_sens_capacity + 1/2 (equip_latent - design_latent)
    #       if total_equip_sens_capacity >= design_sens_load 
    #          AND equip_latent_capcity - 1/2 (excess) > design_latent_load
    #          then system is OK
    #   OR if equip_sensible_capacity < design_sensible_load
    #      BUT/AND fan_speed = +1 level, then check if system meets need
    #   OR if equip_latent_capacity < design_latent_load
    #      BUT/AND fan_speed = -1 level, then check if system meets need
    
    
    
    
    

#enddef

if __name__ == '__main__':
    print("Doing equipment selection (Manual S) standalone....")

    project = configparser.Safeconfigparser()
    project_file = os.path.abspath('projects/man_s_ex3-13.txt')
    project.read(project_file)
        
    equipment_selection(project)
    
#endif