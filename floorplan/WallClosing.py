import cv2
import numpy as np
import os
import sys
import getopt
import copy
from Util import countBlack
from shapely.geometry import Polygon, LineString, MultiLineString
from shapely import ops

def notcovered(interval, ilist):
    to_process = [interval] 
    res = []

    while len(to_process) > 0:
        x = to_process.pop()
        nonempty = True
        for y in ilist:
            if (y[0] > x[0]) and (y[0] <= x[1]):
                if (y[1] < x[1]):
                    to_process.append((y[1]+1, x[1]))
                x = (x[0], y[0] - 1)
            elif (y[0] <= x[0]):
                if (y[1] >= x[1]):
                    nonempty = False
                    break
                elif (y[1] >= x[0]):
                    x = (y[1] + 1, x[1])
        if (nonempty):
           res.append(x)
    return res



def outermost(lines):
    chosenleft = []
    l3 = sorted(lines, key=lambda x: min(x[0][1], x[0][3]))
    l2 = sorted(l3, key=lambda x: min(x[0][0], x[0][2]))
    covered = []
    for l in l2:
        if (abs(l[0][0] - l[0][2]) <= 5) and (abs(l[0][1] - l[0][3]) > 5):
            currange = (min(l[0][1], l[0][3]), max(l[0][1], l[0][3]))
            if (len(notcovered(currange, covered)) > 0):
                covered.append(currange)
                chosenleft.append(l)

    chosenright = []
    l3 = sorted(lines, key=lambda x: -max(x[0][1], x[0][3]))
    l2 = sorted(l3, key=lambda x: -max(x[0][0], x[0][2]))
    covered = []
    for l in l2:
        if (abs(l[0][0] - l[0][2]) <= 5) and (abs(l[0][1] - l[0][3]) > 5):
            currange = (min(l[0][1], l[0][3]), max(l[0][1], l[0][3]))
            if (len(notcovered(currange, covered)) > 0):
                covered.append(currange)
                chosenright.append(l)


    chosentop = []
    l3 = sorted(lines, key=lambda x: min(x[0][0], x[0][2]))
    l2 = sorted(l3, key=lambda x: min(x[0][1], x[0][3]))
    covered = []
    for l in l2:
        if (abs(l[0][0] - l[0][2]) > 5) and (abs(l[0][1] - l[0][3]) <= 5):
            currange = (min(l[0][0], l[0][2]), max(l[0][0], l[0][2]))
            if (len(notcovered(currange, covered)) > 0):
                covered.append(currange)
                chosentop.append(l)

    chosenbottom = []
    l3 = sorted(lines, key=lambda x: -max(x[0][0], x[0][2]))
    l2 = sorted(l3, key=lambda x: -max(x[0][1], x[0][3]))
    covered = []
    for l in l2:
        if (abs(l[0][0] - l[0][2]) > 5) and (abs(l[0][1] - l[0][3]) <= 5):
            currange = (min(l[0][0], l[0][2]), max(l[0][0], l[0][2]))
            if (len(notcovered(currange, covered)) > 0):
                covered.append(currange)
                chosenbottom.append(l)
    return chosenleft, chosenright, chosentop, chosenbottom

def outermost2(lines):
    chosenleft = []
    l3 = sorted(lines, key=lambda x: min(x[0][1], x[0][3]))
    l2 = sorted(l3, key=lambda x: min(x[0][0], x[0][2]))
    covered = []
    for l in l2:
        if (abs(l[0][0] - l[0][2]) <= 5) and (abs(l[0][1] - l[0][3]) > 5):
            currange = (min(l[0][1], l[0][3]), max(l[0][1], l[0][3]))
            nc = notcovered(currange, covered)
            if (len(nc) > 0):
                covered.append(currange)
                for x in nc:
                    l1 = [[l[0][0], x[0], l[0][2], x[1]]]
                    chosenleft.append(l1)

    chosenright = []
    l3 = sorted(lines, key=lambda x: -max(x[0][1], x[0][3]))
    l2 = sorted(l3, key=lambda x: -max(x[0][0], x[0][2]))
    covered = []
    for l in l2:
        if (abs(l[0][0] - l[0][2]) <= 5) and (abs(l[0][1] - l[0][3]) > 5):
            currange = (min(l[0][1], l[0][3]), max(l[0][1], l[0][3]))
            nc = notcovered(currange, covered)
            if (len(nc) > 0):
                covered.append(currange)
                for x in nc:
                    l1 = [[l[0][0], x[0], l[0][2], x[1]]]
                    chosenright.append(l1)


    chosentop = []
    l3 = sorted(lines, key=lambda x: min(x[0][0], x[0][2]))
    l2 = sorted(l3, key=lambda x: min(x[0][1], x[0][3]))
    covered = []
    for l in l2:
        if (abs(l[0][0] - l[0][2]) > 5) and (abs(l[0][1] - l[0][3]) <= 5):
            currange = (min(l[0][0], l[0][2]), max(l[0][0], l[0][2]))
            nc = notcovered(currange, covered)
            if (len(nc) > 0):
                covered.append(currange)
                for x in nc:
                    l1 = [[x[0], l[0][1], x[1], l[0][3]]]
                    chosentop.append(l1)

    chosenbottom = []
    l3 = sorted(lines, key=lambda x: -max(x[0][0], x[0][2]))
    l2 = sorted(l3, key=lambda x: -max(x[0][1], x[0][3]))
    covered = []
    for l in l2:
        if (abs(l[0][0] - l[0][2]) > 5) and (abs(l[0][1] - l[0][3]) <= 5):
            currange = (min(l[0][0], l[0][2]), max(l[0][0], l[0][2]))
            nc = notcovered(currange, covered)
            if (len(nc) > 0):
                covered.append(currange)
                for x in nc:
                    l1 = [[x[0], l[0][1], x[1], l[0][3]]]
                    chosenbottom.append(l1)
    return chosenleft, chosenright, chosentop, chosenbottom


def removeDup(l):
    newlist = []
    for curline in l:
        if (curline[0][0] > curline[0][2]):
            curline[0][0], curline[0][2] = curline[0][2], curline[0][0]
            curline[0][1], curline[0][3] = curline[0][3], curline[0][1]
        res = True
        for y in newlist:
            if (((curline[0][0] == y[0][0]) and  (curline[0][1] == y[0][1]) and  (curline[0][2] == y[0][2]) and  (curline[0][3] == y[0][3])) or ((curline[0][0] == y[0][2]) and  (curline[0][1] == y[0][3]) and  (curline[0][2] == y[0][0]) and  (curline[0][3] == y[0][1]))):
               res = False
               break
        if (res):
           newlist.append(curline)
    return newlist
 

def mergelines(image, chosentop, chosenbottom, chosenleft, chosenright, maxwidth, maxgap):
    ctb = chosentop + chosenbottom
    ctbadj = []
    ctb1 =  sorted(ctb, key=lambda x: min(x[0][1], x[0][3]))
    startpos = 0
    curline = ctb1[0]
    i = 0
    width = maxwidth
    gap = maxgap
    tlen = 0
    while i < len(ctb1):
        ctb2 = []
        ctb2.append(ctb1[i])
        i = i + 1
        while (i < len(ctb1)) and (ctb2[0][0][1] + width >= ctb1[i][0][1]):
            ctb2.append(ctb1[i])
            i = i + 1
        ctb2 =  sorted(ctb2, key=lambda x: x[0][0])
        #print(ctb2)
        curline = ctb2[0]    
        if (curline[0][0] > curline[0][2]):
            curline[0][0], curline[0][2] = curline[0][2], curline[0][0]
            curline[0][1], curline[0][3] = curline[0][3], curline[0][1]
        tlen = tlen + len(ctb2)
        j = 1
        miny = min(curline[0][1], curline[0][3])
        maxy = max(curline[0][1], curline[0][3])
        while j < len(ctb2):
                if (ctb2[j][0][0] < ctb2[j][0][2]):
                    xlow, xhigh = ctb2[j][0][0], ctb2[j][0][2]
                else:
                    xlow, xhigh = ctb2[j][0][2], ctb2[j][0][0]

                if (xlow > curline[0][2] + gap):
                    #print("Curline  " + str(curline))
                    if (miny != maxy):
                        list1 = [countBlack(image, [[curline[0][0], y, curline[0][2], y]]) for y in range(miny, maxy+1)]
                        pos = np.argmax(list1)
                        curline[0][1] = miny + pos
                        curline[0][3] = miny + pos
                    ctbadj.append(curline)
                    if (j < len(ctb2)):
                        curline = ctb2[j]
                        if (curline[0][0] > curline[0][2]):
                            curline[0][0], curline[0][2] = curline[0][2], curline[0][0]
                            curline[0][1], curline[0][3] = curline[0][3], curline[0][1]
                        miny = min(curline[0][1], curline[0][3])
                        maxy = max(curline[0][1], curline[0][3])
                    else:
                        curline = []
                elif (xhigh  > curline[0][2]):
                    curline[0][2] = xhigh
                    miny = min(miny, min(curline[0][1], curline[0][3]))
                    maxy = max(maxy, max(curline[0][1], curline[0][3]))
                j = j + 1
        if (len(curline) > 0):
                #print("Curline  " + str(curline))
                ctbadj.append(curline)

    clr = chosenleft + chosenright
    clr1 =  sorted(clr, key=lambda x: min(x[0][0], x[0][2]))

    startpos = 0
    curline = clr1[0]
    i = 0
    clradj = []
    width = maxwidth
    gap = maxgap
    tlen = 0
    while i < len(clr1):
        clr2 = []
        clr2.append(clr1[i])
        i = i + 1
        while (i < len(clr1)) and (clr2[0][0][0] + width >= clr1[i][0][0]):
            clr2.append(clr1[i])
            i = i + 1
        clr2 =  sorted(clr2, key=lambda x: x[0][1])
        #print(clr2)
        curline = clr2[0]    
        if (curline[0][1] > curline[0][3]):
            curline[0][0], curline[0][2] = curline[0][2], curline[0][0]
            curline[0][1], curline[0][3] = curline[0][3], curline[0][1]
        tlen = tlen + len(clr2)
        j = 1
        minx = min(curline[0][0], curline[0][2])
        maxx = min(curline[0][0], curline[0][2])
        while j < len(clr2):
                if (clr2[j][0][1] < clr2[j][0][3]):
                    ylow, yhigh = clr2[j][0][1], clr2[j][0][1]
                else:
                    ylow, yhigh = clr2[j][0][3], clr2[j][0][3]
                if (ylow > curline[0][3] + gap):
                    #print("Curline  " + str(curline))
                    if (minx != maxx):
                        list1 = [countBlack(image, [[x, curline[0][1], x,  curline[0][3]]]) for x in range(minx, maxx+1)]
                        pos = np.argmax(list1)
                        curline[0][0] = minx + pos
                        curline[0][2] = minx + pos
                    clradj.append(curline)
                    if (j < len(clr2)):
                        curline = clr2[j]
                        if (curline[0][1] > curline[0][3]):
                            curline[0][0], curline[0][2] = curline[0][2], curline[0][0]
                            curline[0][1], curline[0][3] = curline[0][3], curline[0][1]
                        minx = min(curline[0][0], curline[0][2])
                        maxx = min(curline[0][0], curline[0][2])
                    else:
                        curline = []
                elif (yhigh > curline[0][3]):
                    curline[0][3] = yhigh
                    minx = min(minx, (min(curline[0][0], curline[0][2])))
                    maxx = max(maxx, (min(curline[0][0], curline[0][2])))
                j = j + 1
        if (len(curline) > 0):
                #print("Curline  " + str(curline))
                clradj.append(curline)
    return ctbadj, clradj

#
#   find the minimpum euclidean distance between point 1 and the end point of l2
#


def euclidean(a, b):
    return sum( [(x-y)**2 for x, y in zip(a, b)])

def euclid1(p1, l2):
    return min(euclidean(p1, [l2[0][0], l2[0][1]]), euclidean(p1, [l2[0][2], l2[0][3]]))

#
#  check direction of 3 poitns
#
def orientation(p, q, r):
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    return np.sign(val)


#
#  assume p, q, r is coliner, check if q is between p and r
#
def onSegment(p, q, r):
     return (q[0] <= max(p[0], r[0])) and (q[0] >= min(p[0], r[0])) and (q[1] <= max(p[1], r[1])) and (q[1] >= min(p[1], r[1]))

#
#
#  check if two line intersect
#
#
def intersect(l1, l2):
    #print("   check intersect : " + str(l1) + " " + str(l2))
    if (l1[0][0] <= l1[0][2]):
        l1low = [l1[0][0], l1[0][1]]
        l1high = [l1[0][2], l1[0][3]]
    else:
        l1high = [l1[0][0], l1[0][1]]
        l1low = [l1[0][2], l1[0][3]]
    if (l2[0][0] <= l2[0][2]):
        l2low = [l2[0][0], l2[0][1]]
        l2high = [l2[0][2], l2[0][3]]
    else:
        l2high = [l2[0][0], l2[0][1]]
        l2low = [l2[0][2], l2[0][3]]
    o1 = orientation(l1low, l1high, l2low)
    o2 = orientation(l1low, l1high, l2high)
    o3 = orientation(l2low, l2high, l1low)
    o4 = orientation(l2low, l2high, l1high)
    #print("   l1low, l1high, l2low, l2high : " + str(l1low) + " " + str(l1high) + " " + str(l2low) + " " + str(l2high))
    #print("   o1 o2 o3 o4" + str(o1) + " " + str(o2) + " " + str(o3) + " " + str(o4))

    if (o1 != o2) and (o3 != o4):
        return True

    if (o1 == 0  and onSegment(l1low, l2low, l1high)):
        return True

    if (o2 == 0  and onSegment(l1low, l2high, l1high)):
        return True

    if (o3 == 0  and onSegment(l2low,  l1low, l2high)):
        return True

    if (o4 == 0  and onSegment(l2low, l1high, l2high)):
        return True

    return False

def checkIntersect(line, linelist):
    res = False
    for l in linelist:
        if (intersect(line, l)):
            res = True
            break
    return res



def findBoundary(image, c1):

    #i6 = np.zeros((image.shape[0], image.shape[1], 3), np.uint8)
    #i6.fill(255)
    #for l in c1:
    #    for x1, y1, x2, y2 in l:
    #        cv2.line(i6, (x1, y1), (x2, y2), (50, 50, 0), 1)
    #cv2.imshow("res4a", i6)


    ext = []
    extpush = [] 
    minpos = np.argmin([min(l[0][0], l[0][2]) + min(l[0][1], l[0][3]) / 1000000 for l in c1])
    initline = c1[minpos]
    #print(minpos)
    #print(initline)
    c1.pop(minpos)
    curline = initline
    count = 0
    ext.append(curline)
    extpush.append(False)

    #for x1, y1, x2, y2 in curline:
    #    cv2.line(i6, (x1, y1), (x2, y2), (50, 0, 50), 1)
    #filename = "_temp3/count_" + str(count) + ".jpg"
    #cv2.imwrite(filename, i6)

    done = False
    origcount = len(c1)
    #print(c1)
    while (count < 500) and (len(c1) > 0) and (not done):
        #print("Count : " +  str(count) + "  " + str(curline))
        c1a = range(0, len(c1))
        l3 = sorted(c1a, key=lambda x: euclid1([curline[0][2], curline[0][3]], c1[x]))
        found = False
        j = 0
        lnew1 = []
        lnew2 = []
        while (not found) and (j < len(c1a)):
            newline = c1[l3[j]] 
            if (intersect(curline, newline)):
                found = True
                break
            temp = [].append(newline)
            #print("   newline : " + str(newline))
            d1 = euclidean([curline[0][2], curline[0][3]], [newline[0][0], newline[0][1]])
            d2 = euclidean([curline[0][2], curline[0][3]], [newline[0][2], newline[0][3]])
            #print("   d1  d2 " + str(d1) + "  " + str(d2))

            if (d2 < d1):
               newline[0][0], newline[0][1], newline[0][2], newline[0][3] = newline[0][2], newline[0][3], newline[0][0], newline[0][1]
               d1 = d2
            if (d1 > 0):
               lnew_a1 = [[curline[0][2], curline[0][3], curline[0][2], newline[0][1]]]
               lnew_a2 = [[curline[0][2], newline[0][1], newline[0][0], newline[0][1]]]
               lnew_b1 = [[curline[0][2], curline[0][3], newline[0][0], curline[0][3]]]
               lnew_b2 = [[newline[0][0], curline[0][3], newline[0][0], newline[0][1]]]
               black_a = countBlack(image, lnew_a1) + countBlack(image, lnew_a2)
               black_b = countBlack(image, lnew_b1) + countBlack(image, lnew_b2)
               if (black_a > black_b):
                   lnew1 = lnew_a1
                   lnew2 = lnew_a2
               else:
                   lnew1 = lnew_b1
                   lnew2 = lnew_b2
               found = True
               break
               '''
               lnew_a1 = [[curline[0][2], curline[0][3], curline[0][2], newline[0][1]]]
               lnew_a2 = [[curline[0][2], newline[0][1], newline[0][0], newline[0][1]]]
               #print("checking " + str([newline]) + " " + str(lnew1) + str(lnew2))
               intersected_a = checkIntersect(lnew_a1, ext[0:-1]+c1[0:l3[j]]+c1[(l3[j]+1):]+[newline]) or checkIntersect(lnew_a2, ext+c1[0:l3[j]]+c1[(l3[j]+1):]) 
               lnew_b1 = [[curline[0][2], curline[0][3], newline[0][0], curline[0][3]]]
               lnew_b2 = [[newline[0][0], curline[0][3], newline[0][0], newline[0][1]]]
               intersected_b = checkIntersect(lnew_b1, ext[0:-1]+c1[0:l3[j]]+c1[(l3[j]+1):]+[newline]) or checkIntersect(lnew_b2, ext+c1[0:l3[j]]+c1[(l3[j]+1):]) 
               if (not intersected_a):
                  if (not intersected_b):
                       black_a = countBlack(image, lnew_a1) + countBlack(image, lnew_a2)
                       black_b = countBlack(image, lnew_b1) + countBlack(image, lnew_b2)
                       if (black_a > black_b):
                           lnew1 = lnew_a1
                           lnew2 = lnew_a2
                       else:
                           lnew1 = lnew_b1
                           lnew2 = lnew_b2
                  else:
                       lnew1 = lnew_a1
                       lnew2 = lnew_a2
                  found = True
                  break
               elif (not intersected_b):  
                   lnew1 = lnew_b1
                   lnew2 = lnew_b2
                   found = True
                   break
               elif (len(c1) < int(origcount / 4) + 1) and (j <= 3) and (((newline[0][0] == initline[0][0]) and (newline[0][1] == initline[0][1]) and (newline[0][2] == initline[0][2]) and (newline[0][3] == initline[0][3]))  or ((newline[0][0] == initline[0][2]) and (newline[0][1] == initline[0][3]) and (newline[0][2] == initline[0][0]) and (newline[0][3] == initline[0][1]))):
                     found = True
                     break
               j = j+1
               '''
            else:
                lnew = []
                print("no distance : " + str(curline) + str(newline))
                found = True
                break;
        if (not found):
            #print("   Not found")
            lold = ext.pop()
            #for x1, y1, x2, y2 in lold:
            #        cv2.line(i6, (x1, y1), (x2, y2), (50, 50, 0), 1)
            pold = extpush.pop()
            if (pold):
                lold1 = ext.pop()
                lold2 = ext.pop()
                #for x1, y1, x2, y2 in lold1:
                #    cv2.line(i6, (x1, y1), (x2, y2), (30, 30, 200), 1)
                #for x1, y1, x2, y2 in lold2:
                #    cv2.line(i6, (x1, y1), (x2, y2), (30, 30, 200), 1)
            curline = ext[-1]
        else:
            if (len(lnew1) > 0):
               extpush.append(True)
               ext.append(lnew1)
               ext.append(lnew2)
               #print("  add lnew : " + str(lnew))
               #for x1, y1, x2, y2 in lnew1:
               #     cv2.line(i6, (x1, y1), (x2, y2), (50, 50, 50), 1)
               #for x1, y1, x2, y2 in lnew2:
               #     cv2.line(i6, (x1, y1), (x2, y2), (50, 50, 50), 1)
            else:
               extpush.append(False)
            ext.append(newline)
            #print("j = "+ str(j))
            #print(l3)
            c1.pop(l3[j])
            #for x1, y1, x2, y2 in newline:
            #        cv2.line(i6, (x1, y1), (x2, y2), (150, 0, 150), 1)
            curline = newline
        #filename = "_temp3/count_" + str(count) + ".jpg"
        #cv2.imwrite(filename, i6)
        count = count + 1
        if (count == (int(origcount / 5) + 1)):
           c1.append(initline)
        elif (count > (int(origcount / 5) + 1)):
            done = ((curline[0][0] == initline[0][0]) and (curline[0][1] == initline[0][1]) and (curline[0][2] == initline[0][2]) and (curline[0][3] == initline[0][3]))  or ((curline[0][0] == initline[0][2]) and (curline[0][1] == initline[0][3]) and (curline[0][2] == initline[0][0]) and (curline[0][3] == initline[0][1])) 

    # clean up 
    # remove single points
    ext1 = [x for x in ext if (x[0][0] != x[0][2]) or (x[0][1] != x[0][3])]

    # combine colinear lines that are adjacent
    if ((ext1[0][0][0] == ext1[-1][0][0]) and (ext1[0][0][1] == ext1[-1][0][1]) and (ext1[0][0][2] == ext1[-1][0][2]) and (ext1[0][0][3] == ext1[-1][0][3])) or ((ext1[0][0][0] == ext1[-1][0][0]) and (ext1[0][0][1] == ext1[-1][0][1]) and (ext1[0][0][2] == ext1[-1][0][2]) and (ext1[0][0][3] == ext1[-1][0][3])):
        ext1.pop()

    ext2 = [ext1[0]]
    for j in range(1, len(ext1)):
        if (ext2[-1][0][0] == ext2[-1][0][2]) and (ext2[-1][0][2] == ext1[j][0][0]) and (ext1[j][0][0] == ext1[j][0][2]):
            l1min = min(ext2[-1][0][1], ext2[-1][0][3])
            l1max = max(ext2[-1][0][1], ext2[-1][0][3])
            l2min = min(ext1[j][0][1], ext1[j][0][3])
            l2max = max(ext1[j][0][1], ext1[j][0][3])
            if (l1max >= l2min) and (l1max <= l2max):
                ext2[-1][0][1] = l1min
                ext2[-1][0][3] = l2max
            elif (l2max >= l1min) and (l2max <= l1max):
                ext2[-1][0][1] = l2min
                ext2[-1][0][3] = l1max
        elif (ext2[-1][0][1] == ext2[-1][0][3]) and (ext2[-1][0][3] == ext1[j][0][1]) and (ext1[j][0][1] == ext1[j][0][3]):
            l1min = min(ext2[-1][0][0], ext2[-1][0][2])
            l1max = max(ext2[-1][0][0], ext2[-1][0][2])
            l2min = min(ext1[j][0][0], ext1[j][0][2])
            l2max = max(ext1[j][0][0], ext1[j][0][2])
            if (l1max >= l2min) and (l1max <= l2max):
                ext2[-1][0][0] = l1min
                ext2[-1][0][2] = l2max
            elif (l2max >= l1min) and (l2max <= l1max):
                ext2[-1][0][0] = l2min
                ext2[-1][0][2] = l1max

        else:
            ext2.append(ext1[j])

    #print(ext)
    #print(ext1)
    #print(ext2)
    #print(str(len(ext)) + " "  + str(len(ext1)) + "  " + str(len(ext2)))
    return ext2


def equalline(l1, l2):

    if (np.array_equal(l1[0] , l2[0])):
        return True
    else:
        if (np.array_equal(l1[0] , [l2[0][2], l2[0][3], l2[0][0], l2[0][1]])):
           return True
    return False

def line_intersection(line1, line2):
    print("line intersection : " + str(line1) + " " +str(line2))
    l1 = LineString([(line1[0][0], line1[0][1]), (line1[0][2], line1[0][3])])
    l2 = LineString([(line2[0][0], line2[0][1]), (line2[0][2], line2[0][3])])
    p = l1.intersection(l2)
    print("   intersected: " + str(p))
    if (p.geom_type == "LineString"):
        plist = list(p.coords)
        return line2[0][0], line2[0][1]
        


    return int(p.x), int(p.y)


def flipendpt(l):
   return [[l[0][2], l[0][3], l[0][0], l[0][1]]]



def findInternalBoundary(image, lines, ext):

    # first separate the list into selected and unselected
    # first process the external line list into a polygon
    

    allext = []
    ext1 = []
    line1 = ext[0]
    line2 = ext[1]
    print(line1)
    print(line2)
    if ((line1[0][0] == line2[0][0]) and (line1[0][1] == line2[0][1])):
       line1 = flipendpt(line1) 
    elif ((line1[0][0] == line2[0][0]) and (line1[0][2] == line2[0][3])):
       line1 = flipendpt(line1) 
       line2 = flipendpt(line2) 
    elif ((line1[0][2] == line2[0][3]) and (line1[0][2] == line2[0][3])):
       line2 = flipendpt(line2) 
    elif ((line1[0][2] != line2[0][0]) or (line1[0][3] != line2[0][1])):
        if (intersect(line1, line2)):
            x,y = line_intersection(line1, line2)
            line1[0][2] = x
            line1[0][3] = y
            line2[0][0] = x
            line2[0][1] = y
    ext1.append(line1)
    ext1.append(line2)
    print(ext1)
    for i in range(2, len(ext)):
        line1 = ext1[-1]
        line2 = ext[i]
        print(str(line1) + " " + str(line2))
        if ((line1[0][2] == line2[0][2]) and (line1[0][3] == line2[0][3])):
           line2 = flipendpt(line2) 
           print(" flipped " + str(line2))
        elif ((line1[0][2] != line2[0][0]) or (line1[0][3] != line2[0][1])):
            if (intersect(line1, line2)):
                x,y = line_intersection(line1, line2)
                ext1[-1][0][2] = x
                ext1[-1][0][3] = y
                line2[0][0] = x
                line2[0][1] = y
                if (ext1[-1][0][0] == ext1[-1][0][2]) and (ext1[-1][0][1] == ext1[-1][0][3]):
                    ext1.pop()
        for j in range(len(ext1)-2, -1, -1):
            #print("  checking : " + " " + str(i) + "  " + str(j) + "  " + str(ext1[j]))
            if (len(ext1) > 1):
              if (intersect(ext1[j], line2)):
                print("  intersect " + str(j) + "  len(ext1) : " + str(len(ext1)) + " " + str(line2))
                x,y = line_intersection(ext1[j], line2)
                newext = copy.deepcopy(ext1[j:])
                print("    line2 " + str(line2))
                newext.append(copy.deepcopy(line2))
                print("  newext: " + str(newext))
                newext[0][0][0] = x
                newext[0][0][1] = y
                newext[-1][0][2] = x
                newext[-1][0][3] = y
                newext = [x for x in newext if (x[0][0] != x[0][2]) or (x[0][1] != x[0][3])]
                print("  newext: " + str(newext))
                if (len(newext) > 2):
                    allext.append(copy.deepcopy(newext))
                print("    line : " + str(line2))

                ext1[j][0][2] = x
                ext1[j][0][3] = y
                line2[0][0] = x
                line2[0][1] = y
                del ext1[j+1:]
                print("    exp : " + str(line2))
                print("  newext: " + str(newext))
                print("   ext1[-1] : " + str(ext1[-1]))
                if (ext1[-1][0][0] == ext1[-1][0][2]) and (ext1[-1][0][1] == ext1[-1][0][3]):
                    ext1.pop()
        if (line2[0][0] != line2[0][2]) or (line2[0][1] != line2[0][3]):
            ext1.append(line2)
        print("  end of " + str(i) + "  " + str(ext1))
    ext1 = [x for x in ext1 if (x[0][0] != x[0][2]) or (x[0][1] != x[0][3])]
    if (len(ext1) > 2):
       allext.append(copy.deepcopy(ext1))

    print("=====")
    for q in allext:
       print(q)
       print("-----")
    print("=====")

    '''
    grey1 =  np.zeros((image.shape[0], image.shape[1], 3), np.uint8)
    grey1.fill(255)
    for l1 in ext:
       for x1, y1, x2, y2 in l1:
          cv2.line(grey1, (x1, y1), (x2, y2), (0, 0, 85), 15)
    '''


    allpoly = []
    q = 0
    for ext in allext:
        polypts = []
        polypts.append((ext[0][0][0], ext[0][0][1]))
        polypts.append((ext[0][0][2], ext[0][0][3]))
        for l in ext[1:]:
            polypts.append((l[0][2], l[0][3]))
        if (len(polypts) > 2):
            p1 = Polygon(polypts)
            if (p1.boundary.is_simple):
               allpoly.append(p1)
               for l1 in ext:
                   for x1, y1, x2, y2 in l1:
                      #cv2.line(grey1, (x1, y1), (x2, y2), (0, q, q + 20), 8)
                      q = q+23
            else:
                print(str(p1) + " is not simple")
    print(allpoly)

    internal = []
    for l in lines:
        for x1, y1, x2, y2 in l:
            #cv2.line(grey1, (x1, y1), (x2, y2), (75, 0, 75), 1)
            l1 = LineString([(x1, y1), (x2, y2)])
            for p in allpoly:
              if p.contains(l1):
                  internal.append(l)
                  break
    print(internal)
    print(len(internal))
    print(len(lines))
    #cv2.imwrite("_temp2/temp.jpg", grey1);




    '''
    ext1 = [ext[0]]
    for i in range(1, len(ext)):
        l1 = ext[i]
        for j in range(len(ext1) - 1, -1, -1):
            if (intersect(l1, ext1[j])):
                print("Intersected : " + str(i) + " " + str(j))
                x,y = line_intersection(l1, ext1[j])
                del ext1[j+1:]
                ext1[j][0][2] = x
                ext1[j][0][3] = y
                l1[0][0] = x
                l1[0][1] = y
        ext1.append(l1)
    print(ext1)

    '''




    '''
    polypts = []
    line1 = ext[0][0]
    line2 = ext[1][0]
    print(line1)
    print(line2)
    if ((line1[0] == line2[0]) and (line1[1] == line2[1])):
        polypts.append((line1[2], line1[3]))
        polypts.append((line1[0], line1[1]))
        ptb = (line1[0], line1[1])
    elif (line1[2] == line2[0]) and (line1[3] == line2[1]):
        polypts.append((line1[0], line1[1]))
        polypts.append((line1[2], line1[3]))
        ptb = (line1[2], line1[3])
    elif (line1[2] == line2[2]) and (line1[3] == line2[3]):
        polypts.append((line1[0], line1[1]))
        polypts.append((line1[2], line1[3]))
        ptb = (line1[2], line1[3])
    elif (line1[0] == line2[2]) and (line1[1] == line2[3]):
        polypts.append((line1[2], line1[3]))
        polypts.append((line1[0], line1[1]))
        ptb = (line1[0], line1[1])
    else:
        print("INit point error:")
        polypts.append((line1[0], line1[1]))
        polypts.append((line1[2], line1[3]))
        ptb = (line1[2], line1[3])



    for l in ext[1:]:
        lnew = l[0]
        print(lnew)
        if (lnew[0] == ptb[0]) and (lnew[1] == ptb[1]):
           polypts.append((lnew[2], lnew[3]))
           ptb = (lnew[2], lnew[3])
        elif (lnew[2] == ptb[0]) and (lnew[3] == ptb[1]):
           polypts.append((lnew[0], lnew[1]))
           ptb = (lnew[0], lnew[1])
        else:
           print("point point error:")
           polypts.append((lnew[0], lnew[1]))
           polypts.append((lnew[2], lnew[3]))
           ptb = (lnew[2], lnew[3])
    '''


    '''
    print(polypts)
    l1 = LineString(polypts)

    p1 = l1.envelope

    print(p1)


    internal = []

    for l in lines:
        for x1, y1, x2, y2 in l:
            l1 = LineString([(x1, y1), (x2, y2)])
            if extpoly.contains(l1):
                internal.append(l)
    print(internal)
    print(len(internal))
    '''



    '''
    for l in c1:
        found = False
        for j in ext:
            if (equalline(l, j)):
                found = True
                break
        if (not found):
            unselected.append(l)
    print(len(c1))
    print(len(ext))
    print(len(unselected))
    print(c1)
    print("---")
    print(ext)
    print("---")
    print(unselected)
    '''




def WallClosing2(image, houghThreshold = 30, houghMinLength = 100, houghMaxGap = 10, mergeMaxWidth = 8, mergeMaxGap = 15, ofilehead=""):

    # generate line segment via probabilistic Hough Transform

    if (len(image.shape) > 2):
       grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
       grey = image
    edges = cv2.Canny(grey, 50, 150, apertureSize = 3)
    trials = 0
    lines = []
    while (trials < 4) and  ((lines is None) or (len(lines) < 4)):
        lines = cv2.HoughLinesP(edges, rho = 1, theta = np.pi/180, threshold = houghThreshold, minLineLength=houghMinLength, maxLineGap=houghMaxGap)
        #print("number of lines from HoughLines : " + str(len(lines)))
        if (lines is not None) and (len(lines) >=  4):
            # select line that are on the outside (at least one point of the line is either leftmost/rightmost/topmost/bottom-most among its coordinate
            chosenleft, chosenright, chosentop, chosenbottom =  outermost2(lines)
            #print("chosen left/right/top/bottom : " + str(len(chosenleft)) + " " + str(len(chosenright)) + " " + str(len(chosentop)) + " " + str(len(chosenbottom)))
            if ((len(chosenleft) < 1) or (len(chosenright) < 1) or (len(chosentop) < 1) or (len(chosenbottom) < 1)):
                lines = []
        trials = trials + 1
       
    #print(grey.shape)


    if (lines is None) or (len(lines) < 4):
        print(" too few lines : ")
        return image

    if (len(ofilehead) > 0):
       filename = ofilehead + "_lines.jpg"
       grey1 =  np.zeros((grey.shape[0], grey.shape[1], 3), np.uint8)
       grey1.fill(255)
       for l in lines:
           for x1, y1, x2, y2 in l:
               cv2.line(grey1, (x1, y1), (x2, y2), (0, 0, 0), 1)
       cv2.imwrite(filename, grey1);


    #chosenleft, chosenright, chosentop, chosenbottom =  outermost(lines)

    # merge lines that are close to one another (i.e. horizontal lines that are within mergeMaxWidth gap of y-coordiante [similar for vertical lines]
    # also merge lines that have small gaps between them

    ctbadj, clradj = mergelines(grey, chosentop, chosenbottom, chosenleft, chosenright,  mergeMaxWidth, mergeMaxGap)

    # select line that are on the outside again

    chosenleft1, chosenright1, chosentop1, chosenbottom1 =  outermost2(ctbadj + clradj)

    c1 = removeDup(chosenleft1 + chosenright1 + chosentop1 + chosenbottom1)
    c1a = copy.deepcopy(c1)
    #print(len(c1a))

    # find the boundary 


    ext = findBoundary(grey, c1)

    #findInternalBoundary(grey, lines, ext)


    #print("ofilehead : " + ofilehead)
    if (len(ofilehead) > 0):
       filename = ofilehead + "_lines_ext.jpg"
       grey1 =  np.zeros((grey.shape[0], grey.shape[1], 3), np.uint8)
       grey1.fill(255)
       for l in ext:
           for x1, y1, x2, y2 in l:
               cv2.line(grey1, (x1, y1), (x2, y2), (0, 0, 0), 3)
       cv2.imwrite(filename, grey1);
       filename = ofilehead + "_lines_chosen.jpg"
       grey1 =  np.zeros((grey.shape[0], grey.shape[1], 3), np.uint8)
       grey1.fill(255)
       for l in c1a:
           for x1, y1, x2, y2 in l:
               cv2.line(grey1, (x1, y1), (x2, y2), (0, 0, 0), 3)
       cv2.imwrite(filename, grey1);

    image_copy = image
    for l in ext:
        for x1, y1, x2, y2 in l:
            cv2.line(image_copy, (x1, y1), (x2, y2), (0, 0, 0), 3)

    return image_copy


def internal_wall_closing(image, doors, opening_size=1, closing_size=34, offset=0.0):
    image_copy = image.copy()

    for (x, y, width, height) in doors:
        offset_x = offset * width
        offset_y = offset * height
        new_x = max(0, x - int(offset_x))
        new_y = max(0, y - int(offset_y))

        if new_x > image.shape[0]:
            new_x = 0
        if new_y > image.shape[1]:
            new_y = 0

        new_width = max(0, width + int(offset_x * 2.0))
        new_height = max(0, height + int(offset_y * 2.0))

        if new_x + new_width > image.shape[0]:
            new_width = image.shape[0] - new_x
        if new_y + new_height > image.shape[1]:
            new_height = image.shape[1] - new_y

        # copy the door
        door = image_copy[new_x: new_x + new_width, new_y: new_y + new_height]
        open_dilated = Util.dilate(door, opening_size)
        open_eroded = Util.erode(open_dilated, opening_size)
        close_eroded = Util.erode(open_eroded, closing_size)
        close_dilated = Util.dilate(close_eroded, closing_size)

        # copy rect back to image
        image_copy[new_x: new_x + new_width, new_y: new_y + new_height] = close_dilated

        # cv2.imshow("closing doors...", image2)
        # cv2.waitKey(0)
        # cv2.rectangle(image2, (x - 10, y - 10), (x + w, y + h), (0, 0, 0), -1)

    # cv2.imshow("closing internal wall", image2)
    # cv2.imwrite("internalClosing.png", image2)
    # cv2.waitKey(0)
    return image_copy



