import cv2
import numpy as np
from shapely.geometry import Polygon, LineString
from CalArea import calArea, genPoly




def inverse_color(image):
    height, width = image.shape
    img2 = image.copy()

    for i in range(height):
        for j in range(width):
            img2[i, j] = (255 - image[i, j])
    return img2


def room_detection(image, minroomsize, ifile=''):
    #cv2.imshow('Room Detection Input : ', image) 
    img = image.copy()
    if (len(img.shape) > 2):
       img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    #cv2.imshow('Before : ', thresh) 
    # height, width = thresh.shape
    # thresh2 = thresh.copy()
    # for i in range(height):
    #     for j in range(width):
    #         thresh2[i, j] = (255-thresh2[i, j])


    #contours, hier = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #
    #   find all (nested) contours
    #   check if top level contours has only one room
    #   if so, try using second level contours (if exist)
    #
    contours, hier = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #print(contours)
    #print(hier)
    #print(len(contours))
    #print(len(hier))

    nochild = []
    for i in range(0, len(hier[0])):
        if (hier[0][i][2] == -1):
            nochild.append(i)

    # 0 is valid
    # 1 is invalid
    # 2 is invalid becasuse some of its child is valid
    valid = []
    for i in contours:
        if (len(i) > 2) and (calArea(i) >= minroomsize):
            valid.append(0)
        else:
            valid.append(1)

    #print(valid)

    for i in range(len(valid) - 1 , -1, -1):
        if (valid[i] == 0):
           if (hier[0][i][2] > -1):
              k = hier[0][i][2]
              while (k > 0) and (valid[i] == 0):
                  if (valid[k] == 0) or (valid[k] == 2):
                     valid[i] = 2
                     break
                  else:
                     k = hier[0][k][0]
    #print(valid)

    c1 = [contours[y] for y in range(0, len(valid)) if valid[y] == 0]

    #print(c1)

    '''
    # add rooms from higher level with lower level rooms removed
    for i in range(len(valid) - 1 , -1, -1):
        if (valid[i] == 2):
            print("i : " + str(i))
            poly1 = genPoly(contours[i])
            k = hier[0][i][2]
            while (k > 0):
                print("  k : " + str(k))
                if (valid[k] != 1):
                   poly2 = genPoly(contours[k])
                   poly1 = poly1.difference(poly2)
                k = hier[0][k][0]
            l1 = list(poly1.exterior.coords)
            newc = []
            for a in l1:
                new0  = []
                new0.append(int(a[0]))
                new0.append(int(a[1]))
                newc.append([new0])
            print(poly1)
            print(newc)
            c1.append(newc)
    # for cnt in contours:

    #print(c1)
    '''
    contours = np.array(c1)
    rooms = []
    counter = 0
    for i in contours:
        #print("  i : " + str(i))
        leftmost = tuple(i[:, 0][i[:, :, 0].argmin()])
        rightmost = tuple(i[:, 0][i[:, :, 0].argmax()])
        if (leftmost[0] <= 0) or (rightmost[0] >= img.shape[1] - 1):
            continue
        rooms.append(i)
        counter += 1
    rooms = [x for x in rooms if len(x) > 2]



    # return all rooms that is not overlapping with others

    '''
    polylist= []
    for x in rooms:
        print(x)
        print("====")
        plist = []
        for y in x:
            plist.append(y[0][0])
            plist.append(y[0][1])
        print(plist)
        p = gen_Poly(plist)
        print(p)
        polylist.append(p)
    rooms2 = []
    for i in range(0, len(polylist)):
        res = True
        for j in range(0, len(polylist)):
            if (i != j) and (polylist[i].intersects(polylist[j])):
                res = False
                break
        if (res):
            rooms2.append(rooms[i])
    '''


    return rooms
