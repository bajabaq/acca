import configparser

def system_presentation(project):
    project_name = project.get('Location', 'project_name')            
    print("\tHere is the output, showing worksheets, design info, etc. for " + project_name)
    
#enddef

#other presentation formats go here - like worksheets, layouts, etc

if __name__ == '__main__':
    print("doing this standalone")
    
#endif