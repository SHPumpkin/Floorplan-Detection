import cv2
import Util
import numpy as np


def morphological(image, threshold=100, opening_size=1, closing_size=30): # opening -> one big room
    image_copy = image.copy()
    ret, image_copy = cv2.threshold(image_copy, threshold, 255, cv2.THRESH_BINARY)

    # opening
    open_dilated = Util.dilate(image_copy, opening_size)
    open_eroded = Util.erode(open_dilated, opening_size)

    # closing
    close_eroded = Util.erode(open_eroded, closing_size)
    close_dilated = Util.dilate(close_eroded, closing_size)
    return close_dilated

def morphological2(image, threshold=100, opening_size=1, closing_size=30): # opening -> one big room
    f1 = open("orig", "w")
    f2 = open("d1", "w")
    image_copy = image.copy()
    print(opening_size)
    print(closing_size)
    '''
    print(image_copy)
    count = 0
    for x in image_copy:
        count = count + 1
        f1.write(str(count))
        f1.write(" : ")
        for y in x:
           f1.write(np.array2string(y))
           f1.write(" ")
        f1.write("\n---\n")
    print("Done 0\n")
    '''
    ret, image_copy = cv2.threshold(image_copy, threshold, 255, cv2.THRESH_BINARY)
    cv2.imshow("after threshold: ", image_copy)

    # opening
    open_dilated = Util.dilate(image_copy, opening_size)
    '''
    print(open_dilated)
    count = 0
    for x in open_dilated:
        count = count + 1
        f2.write(str(count))
        f2.write(" : ")
        for y in x:
           f2.write(np.array2string(y))
           f2.write(" ")
        f2.write("\n---\n")
    '''
   

    cv2.imshow("after dilate 1 : " + str(opening_size), open_dilated)
    open_eroded = Util.erode(open_dilated, opening_size)
    cv2.imshow("after erode 1 : " + str(opening_size), open_eroded)

    # closing
    close_eroded = Util.erode(open_eroded, closing_size)
    cv2.imshow("after erode 2 : " + str(closing_size), close_eroded)
    close_dilated = Util.dilate(close_eroded, closing_size)
    cv2.imshow("after dilated 2 : " + str(closing_size), close_dilated)
    cv2.waitKey(0)
    f1.close()
    f2.close()
    return close_dilated
