"""
params: apple_data ((x, y, z), radius)
return: xxxx.xyyyy.yzzzz.zrrrr.r
"""
def apple_data_to_str(apple_data):
    x,y,z,radius = apple_data
    xStr = str(round(1000*abs(x), 1)).rjust(6, "0")
    if x>=0: 
        xStr = "+" + xStr
    else:
        xStr = "-" + xStr
    yStr = str(round(1000*abs(y), 1)).rjust(6, "0")
    if y>=0: 
        yStr = "+" + yStr
    else:
        yStr = "-" + yStr
    zStr = str(round(1000*abs(z), 1)).rjust(6, "0")
    if z>=0: 
        zStr = "+" + zStr
    else:
        zStr = "-" + zStr
    radius = "+" + str(round(1000*radius, 1)).rjust(6, "0")
    return xStr + yStr + zStr + radius

def str_to_coordinate(coordStr):
    x, y, z = (float(coordStr[0:6]), float(coordStr[6:12]), float(coordStr[12: 18]))
    return (x, y, z)

"""
args: x&y&z
unit: mm*10
"""
def parse_url_parameter(args):
    xyz=args.split("&")
    return (int(xyz[0])/10000,int(xyz[1])/10000,int(xyz[2])/10000)