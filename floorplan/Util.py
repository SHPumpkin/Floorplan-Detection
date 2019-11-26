import cv2
from math import ceil, floor


def erode(image, erode_size):
    if erode_size % 2 == 0:
        erode_size = erode_size + 1
    element = cv2.getStructuringElement(cv2.MORPH_RECT, (int(2 * erode_size + 1), int(2 * erode_size + 1)))
    image_copy = image.copy()
    return cv2.erode(image_copy, element)


def dilate(image, dilation_size):
    if dilation_size % 2 == 0:
        dilation_size = dilation_size + 1
    element = cv2.getStructuringElement(cv2.MORPH_RECT, (int(2 * dilation_size + 1), int(2 * dilation_size + 1)))
    image_copy = image.copy()
    return cv2.dilate(image_copy, element)

#
#   assume l is a horizontal or vertical line
#   count the number of black pixel in image on the line
#
def countBlack(image, l):
    #print(image.shape)
    #print(l)
    count = 0
    if (l[0][0] == l[0][2]):
        for y in range(min(l[0][1], l[0][3]), max(l[0][1], l[0][3])+1):
            if (image[y][l[0][0]] == 0):
                count = count + 1
    elif (l[0][1] == l[0][3]):
        for x in range(min(l[0][0], l[0][2]), max(l[0][0], l[0][2])+1):
            if (image[l[0][1]][x] == 0):
                count = count + 1
    else: 
        ydiff = l[0][3] - l[0][1]
        xdiff = l[0][2] - l[0][0]
        diffratio = ydiff / xdiff
        for x in range(min(l[0][0], l[0][2]), max(l[0][0], l[0][2])+1):
            yval = (x - l[0][0]) * diffratio + l[0][1]
            c1 = ceil(yval)
            f1 = floor(yval)
            if (image[f1][x] == 0) or (image[c1][x] == 0):
               count = count + 1
    #print("   count : " +str(count))
    #i1 = image.copy()
    #for x1, y1, x2, y2 in l:
    #   cv2.line(i1, (x1, y1), (x2, y2), (120, 0 , 120), 3)
    #cv2.imshow("img1", i1)
    #cv2.waitKey(0)
    return count

