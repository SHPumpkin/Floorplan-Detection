import cv2
import ObjectDetection
import MorphologicalTransformation
import WallClosing
import RoomDetection
import random
import os
import Util
import numpy as np
from CalArea import calArea, genPoly
from shapely.geometry import Polygon, LineString
import pytesseract
from pytesseract import Output

def text_preprocess(image):
    textdata=pytesseract.image_to_data(image, lang='eng', config='--oem 2', output_type=Output.DICT)
    iarea = image.shape[0] * image.shape[1]
    if (len(image.shape) == 3):
        iarea = iarea / 3
    #print(textdata)
    x = [s for s in textdata['text'] if s]
    a = [i for i ,s in enumerate(textdata['text']) if s]
    #print(x)
    #print(a)
    textlist = []
    for y in a:
        if (not textdata['text'][y].isspace()):
            boundary= (textdata['left'][y], textdata['top'][y], textdata['left'][y] + textdata['width'][y],  textdata['top'][y]+textdata['height'][y])
            #print(textdata['left'][y])
            #print(textdata['top'][y])
            #print(textdata['width'][y])
            #print(textdata['height'][y])
            area = textdata['width'][y] * textdata['height'][y]
            if (area <= iarea/10):
                cv2.rectangle(image, (textdata['left'][y], textdata['top'][y]), (textdata['left'][y] + textdata['width'][y],  textdata['top'][y]+textdata['height'][y]), color=(255, 255, 255), thickness=-1)
            textlist.append([textdata['text'][y], boundary])
    #print(len(textdata['text']))
    #print(len(x))
    return [image, textlist]


def countZero(a):
    res = []
    count = 0
    for x in a:
        if (x == 0):
            count = count + 1
        else:
            if (count > 0):
                res.append(count)
                count = 0
    return res

def countZero1(a):
    res = []
    count = 0
    non_white = -1
    for x in a:
        if (x == 0):
            count = count + 1
            if (non_white == -1):
                non_white = 0
        else:
            if (non_white == 0):
                non_white = 1
            elif (non_white == 1):
                if (count > 0):
                    res.append(count)
                    count = 0
                non_white = -1
    return res

def fillRow(image, i2, mincount):

  for i in range(0, image.shape[0]):
    count = 0
    for j in range(0, len(image[i])):
        if (image[i][j] == 0):
            count = count + 1
        else:
            if (count >= mincount ):
                #print(str(i) + " " +  str(j) + " " +  str(mincount) + " " +  str(count))
                i2[i][j-count-1:j-1] = image[i][j-count-1:j-1]
            count = 0

def fillColumn(image, i2, mincount):

  for i in range(0, image.shape[1]):
    count = 0
    for j in range(0, image.shape[0]):
        if (image[j][i] == 0):
            count = count + 1
        else:
            if (count >= mincount ):
                #print(str(i) + " " +  str(j) + " " +  str(j-count-1) + "  " + str(j-1) + " " +str(mincount) + " " +  str(count))
                for q in range(j-count-1, j):
                   i2[q][i]  = image[q][i]
            count = 0

def thickLines1(image):

    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, grey = cv2.threshold(grey,  127, 255, cv2.THRESH_BINARY)

    hori1 = []

    for x in range(0, grey.shape[0]):
       hori1 = hori1 + countZero1(grey[x])

    for y in range(0, grey.shape[1]):
       hori1 = hori1 + countZero1(grey[:,y])

    hori1.sort()
    h1 = [hori1[x] for x in range(1, len(hori1) - 1) if hori1[x] != hori1[x+1]] + [hori1[len(hori1) - 1]]

    i2 = grey.copy()
    i2.fill(255)
    fillRow(grey, i2, h1[int(len(h1)/3)])
    fillColumn(grey, i2, h1[int(len(h1)/3)])
    #cv2.imshow("grey", grey)
    #cv2.imshow("i2", i2)
    #cv2.waitKey(0)
    return i2




def evaluate(l, minroomsize, isize):
    polylist = [genPoly(x) for x in l]
    arealist = [x.area for x in polylist]
    largearea = [y for y in range(0, len(arealist)) if arealist[y] >= minroomsize]
    a = sum([x for x in arealist if x >= minroomsize])
    l2 = [l[i] for i in largearea]
    return [l2, len(l2) + a/(isize + 10)] 

def evaluate_area(l, minroomsize, isize):
    polylist = [genPoly(x) for x in l]
    arealist = [x.area for x in polylist]
    largearea = [y for y in range(0, len(arealist)) if arealist[y] >= minroomsize]
    a = sum([x for x in arealist if x >= minroomsize])
    l2 = [l[i] for i in largearea]
    return [l2,  a + len(l2)/1000.0] 

def evaluate_closest(l, minroomsize, isize, expected_room):
    polylist = [genPoly(x) for x in l]
    arealist = [x.area for x in polylist]
    largearea = [y for y in range(0, len(arealist)) if arealist[y] >= minroomsize]
    a = sum([x for x in arealist if x >= minroomsize])
    l2 = [l[i] for i in largearea]
    diff = abs(len(l2) - expected_room)
    return [l2,  -(diff + 1.0/(a + 2.0))] 



def detect_rooms(image_file, num_of_trials=100, num_of_rooms = 100, idir = ''):
    run_all_trials = False
    if (num_of_rooms < 0):
        num_of_rooms = -num_of_rooms
        run_all_trials = True
    print("Enter detect Rooms")
    image = cv2.imread(image_file)
    #[image, textlist] = text_preprocess(image)
    print("Done text")
    if (len(image.shape) == 3):
        isize = image.size / 3
    else:
        isize = image.size
    minroomsize = isize / 1000
    print(minroomsize)
    #num_of_rooms = int(input("How many rooms are there in this floor plan?:"))

    output_dir = "_" + image_file.replace(".", "_") + "_" + repr(num_of_trials) + "_13"
    # print(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    result = {}
    output_file = "res_" + image_file.replace(".", "_") + "_" + str(num_of_trials) + ".txt"
    file = open(output_file, "w")

    y = image.shape[0]
    x = image.shape[1]

    trending = [0, 0, -1, 1, -1, 1]
    trend = 1
    pre_rand = [0, 0, 0, 0, 0, 0]
    #room_img_res = image
    room_img_res = []
    pre_poly = []

    # check for the right morophological transform parameters range

    #imageLines = thickLines1(image);

    # pick open parameters such that after dilation there is at least 5% non-white pixels (whiteratio <= 0.95)
    dilate_max = 1
    for i in range(10, 1, -1):
        open_dilated = Util.dilate(image, i)
        hist = cv2.calcHist([open_dilated], [0], None, [256], [0, 256])
        if (len(open_dilated.shape) == 3):
           isize = open_dilated.size / 3
        else:
           isize = open_dilated.size
        whiteratio = hist[255][0] * 1.0 / isize
        #print(str(i) + " " + str(whiteratio))
        if (whiteratio <= 0.95):
            dilate_max = i
            break
    #print("dilate_max : " + str(dilate_max))

    # pick close parameters such that after dilation there is between 5% non-black pixels (blackratio <= 0.95)
    open_dilated = Util.dilate(image, dilate_max)
    open_eroded = Util.erode(open_dilated, dilate_max)

    erode_max = 1
    for i in range(100, 1, -1):
        closed_eroded = Util.erode(open_eroded, i)
        hist = cv2.calcHist([closed_eroded], [0], None, [256], [0, 256])
        if (len(closed_eroded.shape) == 3):
           isize = open_eroded.size / 3
        else:
           isize = open_eroded.size
        blackratio = hist[0][0] * 1.0 / isize
        #print(str(i) + " " + str(blackratio))
        if (blackratio <= 0.95):
            erode_max = i
            break
    #print("erode_max : " + str(erode_max))
    erode_min = 15
    if (erode_max < 30):
        erode_max = 30
        erode_min = 5

    print("Done check dilate")

        

    maxeval = -1
    maxevalarea = -1
    maxevalclosest = -1000000
    curbest_room = []
    curbest_area = []
    curbest_closet = []

    for i in range(0, num_of_trials):
        print("Enter loop")
        rand = [random.uniform(1, 5), random.randint(1, 5), random.randint(0, dilate_max), random.randint(erode_min, erode_max), random.randint(1, 50), random.randint(1, 50)]
        print(rand[0], rand[1], rand[2], rand[3], rand[4], rand[5])
        img = image.copy()
        if (len(idir)  > 0):
           outfile = "_temp2/out_res1_" + str(i) + "_" + str(rand[2]) + "_" + str(rand[3]) + ".jpg"
           cv2.imwrite(outfile, img)

        # print("   Doors detection : " + repr(rand1) + "  " + repr(rand2))
        #doors = ObjectDetection.door_detection(img, scale_factor=rand[0], min_neighbors=rand[1])
        # doors = ObjectDetection.door_detection(img)
        doors = []

        # print("   Morphological Transform : " + repr(rand3) + "  " +  repr(rand4))
        res2 = MorphologicalTransformation.morphological(img, opening_size=rand[2], closing_size=rand[3])
        # res2 = MorphologicalTransformation.morphological(img)



        outfile = "_temp2/out_" + str(i) + "_res2_" + str(rand[2]) + "_" + str(rand[3]) + ".jpg"
        if (len(idir)  > 0):
           outfile = "_temp2/out_res2_" + str(i) + "_" + str(rand[2]) + "_" + str(rand[3]) + ".jpg"
           cv2.imwrite(outfile, res2)
        print("Done res2")

        # print("-- res2 ---\n")
        # print(res2)
        #res3 = WallClosing.convex_wall_closing(res2)
        outfilehead = ""
        if (len(idir)  > 0):
           outfilehead = "_temp2/out_res3a_" + str(i) + "_" + str(rand[2]) + "_" + str(rand[3]) 
        res3 = WallClosing.WallClosing2(res2, houghMinLength=50, ofilehead=outfilehead)
        # print("-- res3 ---\n")
        # print(res3)
        if (len(idir)  > 0):
           outfile = "_temp2/out_res3_" + str(i) + "_" + str(rand[2]) + "_" + str(rand[3]) + ".jpg"
           cv2.imwrite(outfile, res3)
        print("Done res3")

        # print("   Internal wall closing : " + repr(rand5) + "  " + repr(rand6))
        res4 = WallClosing.internal_wall_closing(res3, doors, opening_size=rand[4], closing_size=rand[5])
        #outfile = "_temp2/out_" + str(i) + "_res4_" + str(rand[2]) + "_" + str(rand[3]) + "_" + str(rand[4]) + "_" + str(rand[5]) + ".jpg"
        #cv2.imwrite(outfile, res4)

        # print("-- res4 ---\n")
        # print(res4)
        outfile = ""
        if (len(idir) > 0):
           outfile = "_temp2/out_res4_" + str(i) + "_" + str(rand[2]) + "_" + str(rand[3]) + ".jpg"
        contours = RoomDetection.room_detection(res4, minroomsize, outfile)
        print("Done res4")

        if (len(contours), len(doors)) in result.keys():
            result[(len(contours), len(doors))] += 1
        else:
            result[(len(contours), len(doors))] = 1
        file.write(str(i) + " : Total Rooms : " + str(len(contours)) + "  Total Doors : " + str(len(doors)) + "\n")

        # if abs(num_of_rooms - len(contours)) > 2:
        #   continue

        # writing the result of this run to a file
        #output_file = output_dir + "/" + str(i) + ".jpg"
        #output_file_final = output_dir + "/" + str(i) + "_res.jpg"
        #add_file_final = output_dir + "/" + str(i) + "_add.jpg"
        #cv2.imwrite(output_file, res4)
        room_img = np.zeros((y, x, 3))
        #print(room_img.shape, image.shape)
        img2 = image.astype(float)
        room_img.fill(255)
        c = 0
        for p in contours:
            l = []
            for q in p:
                for t in q:
                    l.append(t)
            # print(l)
            l1 = np.array(l, np.int32)
            cv2.fillPoly(room_img, [l1], ((19 + 7 * c) % 251, (23 + 29 * c) % 251, (89 + 17 * c) % 251))
            c = c + 1
        #cv2.imwrite(output_file_final, room_img)
        #img_add = cv2.addWeighted(img2, 0.3, room_img, 0.7, 0)
        #cv2.imwrite(add_file_final, img_add)

        # calculating results
        if (len(contours) > len(room_img_res)):
            room_img_res = contours

        room_img_res, eval1 = evaluate(room_img_res, minroomsize, isize) 
        room_img_resarea, evalarea = evaluate_area(room_img_res, minroomsize, isize) 
        room_img_resclosest, evalclosest = evaluate_closest(room_img_res, minroomsize, isize, num_of_rooms) 
        if (evalclosest > maxevalclosest):
            maxevalclosest = evalclosest
            curbest_closest = room_img_resclosest
            print("Rooms   curbest_room (closest) : " + str(len(room_img_resclosest)) + "   " + str(maxevalclosest))
        if (evalarea > maxevalarea):
            maxevalarea = evalarea
            curbest_area = room_img_resarea
            print("Rooms   curbest_room (area) : " + str(len(room_img_resarea)) + "   " + str(maxevalarea))
        if (eval1 > maxeval):
            maxeval = eval1
            curbest_room = room_img_res
            print("Rooms   curbest_room : " + str(len(room_img_res)) + "   " + str(maxeval))
            if (not run_all_trials) and (maxeval >= num_of_rooms):
                break

    file.close()
    print("Area")
    for x in curbest_room:
        print(calArea(x))
    print("----")
    textlist = ""
    return [curbest_room, textlist, curbest_area, curbest_closest]

