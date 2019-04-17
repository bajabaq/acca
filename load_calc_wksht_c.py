
#------------------------------------------------------------------------------
#   Worksheet C: Skylights
#------------------------------------------------------------------------------

def output_worksheet_c(results):
    msg = ""
    msg = msg +  60 * "=" + "\n"
    msg = msg +  "Worksheet C: Skylights\n"
    for skylight in results:    
        msg = msg +  60 * "-\n" 
    #endfor
    msg = msg +  60 * "=" + "\n"
    print(msg)
#enddef

def worksheet_c(settings, project, a_results):
    results = {}
    
    output_worksheet_c(results)
    
    return results
#enddef
