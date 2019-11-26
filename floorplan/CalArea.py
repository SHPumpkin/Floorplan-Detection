from shapely.geometry import Polygon, LineString

def calArea(l):
    x = Polygon([(x[0][0], x[0][1]) for x in l])
    return x.area

# take a single list of number, x[0], y[0], x[1], y[1] ..... as input
def calArea2(l):
    x = Polygon([(l[i], l[i+1]) for i in range(0, len(l), 2)])
    return x.area

def genPoly(l):
    return(Polygon([(x[0][0], x[0][1]) for x in l]))

