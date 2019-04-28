"""
params: apple_data ((x, y, z), radius)
return: xxxx.xyyyy.yzzzz.zrrrr.r
"""
def apple_data_to_str(apple_data):
    x,y,z,radius = apple_data
    xStr = str(round(1000*x, 1)).rjust(6, "0")
    if x>=0: 
        xStr = "+" + xStr
    yStr = str(round(1000*y, 1)).rjust(6, "0")
    if y>=0: 
        yStr = "+" + yStr
    zStr = str(round(1000*z, 1)).rjust(6, "0")
    if z>=0: 
        zStr = "+" + zStr
    radius = "+" + str(round(1000*radius, 1)).rjust(6, "0")
    return xStr + yStr + zStr + radius

def str_to_coordinate(coordStr):
    x, y, z = float(coordStr[0:5]), float(coordStr[5:10]), float(coordStr[10: 15])
    return (x, y, z)