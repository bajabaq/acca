

def get_conditioned_floor_area(project, zone_section, cond_type):
    sqft = 0
    list_floors_cond_type  = project.get(zone_section, 'floors_'+cond_type).split(',')
    list_pfloors_cond_type = project.get(zone_section, 'p_floors_'+cond_type).split(',')
    print(cond_type)
    print("x" + str(list_floors_cond_type))
    print("y" + str(list_pfloors_cond_type))

#    print "regular"
    for f in list_floors_cond_type:
        if int(f) > 0:
            floor_section = zone_section + " Floor " + str(f)
            length = float(project.get(floor_section, 'length'))
            width  = float(project.get(floor_section, 'width'))
            area = length * width
            sqft = sqft + area
        #endif
    #endfor

#    print "partition"
    for p in list_pfloors_cond_type:
        if int(p) > 0:
            floor_section = zone_section + " PFloor " + str(p)
            length = float(project.get(floor_section, 'length'))
            width  = float(project.get(floor_section, 'width'))
            area = length * width
            sqft = sqft + area
        #endif
    #endfor

    return sqft
#enddef

