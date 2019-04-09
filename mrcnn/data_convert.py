"""
params: apple_data ((x, y, z), radius)
return: xxxx.xyyyy.yzzzz.zrrrr.r
"""
def apple_data_to_str(apple_data):
    x,y,z = apple_data[0]
    radius = apple_data[1]
    xStr = str(round(1000*x, 1)).rjust(6, "0")
    yStr = str(round(1000*y, 1)).rjust(6, "0")
    zStr = str(round(1000*z, 1)).rjust(6, "0")
    radius = str(round(1000*radius, 1)).rjust(6, "0")
    return xStr + yStr + zStr + radius