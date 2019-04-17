import configparser
import os
import sqlite3


#------------------------------------------------------------------------------
#Get database filename
#this might should be in own module vs copy in each source file
#------------------------------------------------------------------------------
def get_db_filename(settings):
    db_path         = settings.get('system','data_dir')
    db_filename_org = settings.get('system','database')
    cwd = os.getcwd()
    db_filename     = os.path.relpath(db_path + '/' + db_filename_org, cwd)
    if os.path.basename(cwd) != 'acca':
        db_filename = os.path.relpath('../' + db_path + '/' + db_filename_org)
    #endif    
    return db_filename
#enddef


def do_query(settings, SQL, variables):
    db_filename = get_db_filename(settings)
    #db_filename = '..\\data\\acca3.sqlite'
        
    conn = sqlite3.connect(db_filename)    
    cursor = conn.cursor()    
    cursor.execute(SQL, variables)
    results = cursor.fetchall()
    conn.close()
    
    return results
#enddef