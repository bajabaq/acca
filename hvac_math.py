

#------------------------------------------------------------------------------
# from https://en.wikipedia.org/wiki/Linear_interpolation
# (y - y0) / (x - x0) = (y1 - y0) / (x1 - x0)
# rearrange: 
# y - y0 = (y1 - y0) * (x - x0) / (x1 - x0)
#------------------------------------------------------------------------------
def interpolate_val(y2, y1, x2, x1, x):
    y = y1 + (y2 - y1)*(x - x1)/(x2 - x1)    
    return y
#enddef

#------------------------------------------------------------------------------
#extrapolate_value based on 2 points (have to get nearest points)
#------------------------------------------------------------------------------
def extrapolate_val(y2, y1, x2, x1, x):
    y = interpolate_val(y2, y1, x2, x1, x)    
    return y
#enddef


#------------------------------------------------------------------------------
# round a value to a specified base (eg by 5s)
#------------------------------------------------------------------------------
def round_val(x, base=5):
    return int(base * round(float(x)/base))

#I think this is an attempt to implement the +1 -1 or +2 -2 rounding method
#------------------------------------------------------------------------------
# round ctd down if diff between round_low (lower multiple of 5) and ctd <=1
#           up   if diff between round_high (higher multiple of 5) > 1
#------------------------------------------------------------------------------
def round_ctd(ctd):
    rctd       = round(ctd)
    mod5       = rctd % 5
    round5_low = ctd - mod5
    round5_up  = round5_low + 5
    diff       = abs(rctd - round5_low)
    print(diff)
    if diff <= 1:
        round_ctd = round5_low
    else:
        round_ctd = round5_up
    #endif

    return round_ctd
#enddef

#------------------------------------------------------------------------------
# round htd up   if diff between round_low (lower multiple of 5) and htd <=1
#           down if diff between round_high (higher multiple of 5) > 1
#------------------------------------------------------------------------------
def round_htd(htd):
    rhtd       = round(htd)
    mod5       = rhtd % 5
    round5_low = htd - mod5
    round5_up  = round5_low + 5
    diff       = abs(rhtd - round5_low)
    print(diff)
    if diff <= 1:
        round_htd = round5_up
    else:
        round_htd = round5_low
    #endif

    return round_htd
#enddef
