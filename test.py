from math import *

a = atan2(1, 1)
d = degrees(a)

d += 1 * 90
if d > 180:
    d -= 360
print(d)