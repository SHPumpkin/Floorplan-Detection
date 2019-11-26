import cv2
import DetectRooms
import Annotator
import os
import sys
import getopt
import pytesseract
import re
import TextPostProcess
import numpy as np
import time
from CalArea import calArea, calArea2
# TODO: (1) Smooth (2) extend wall (4)combining rooms


'''
def text_preprocess(image):
    textdata=pytesseract.image_to_data(image, lang='eng', config='--oem 2', output_type=Output.DICT)
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
            cv2.rectangle(image, (textdata['left'][y], textdata['top'][y]), (textdata['left'][y] + textdata['width'][y],  textdata['top'][y]+textdata['height'][y]), color=(255, 255, 255), thickness=-1)
            textlist.append([textdata['text'][y], boundary])
    #print(len(textdata['text']))
    #print(len(x))
    return [image, textlist]
'''


    
# Main BUDAS program
command = '''
Command: python3 BUDAS.py <options> image_file 

options: 
  -h                   : print list of parameters and exit
  -b                   : batch processing, save detection result and exit 
  -B                   : save the image with all the rooms blacked out (file name with "black_" attached in front)
  -W                   : save the image with all the rooms whited out (file name with "white_" attached in front)
  -t <number>          : # of trials for detection algorithm (default 100) 
  -r <number>          : minimum # of rooms to detect (default 100)
  -s <directory>       : director to store the result files
  -i <directory>       : save intermediate images in subdirectory
'''

#print(command)
        

# Get Input File Name

image_file = "test.jpg"
result_dir = ""
intermediate_dir = ""
num_of_trials = 100
num_of_rooms = 100
saveBlacked = False
saveWhited = False
batch_process = False

[optlist, filelist] = getopt.getopt(sys.argv[1:], "bhs:t:r:i:BW")
for x,y in optlist : 
    print(x)
    if (x == '-b'):
        batch_process = True
    elif (x == '-t'):
        num_of_trials = int(y)
    elif (x == '-r'):
        num_of_rooms = int(y)
    elif (x == '-s'):
        result_dir = y
    elif (x == '-i'):
        intermediate_dir = y
    elif (x == '-B'):
        saveBlacked = True
    elif (x == '-W'):
        saveWhited = True
    elif (x == '-h'):
        print(command)
        exit()
if (len(filelist) > 0):
    image_file = filelist[0]


print(num_of_trials)


image = cv2.imread(image_file)
image0 = image.copy()

#timestart = time.clock()
timestart = time.perf_counter()

[room_img_res, textlist, room_img_res_area, room_img_res_closest] = DetectRooms.detect_rooms(image_file, num_of_trials, num_of_rooms, intermediate_dir)


#timeend = time.clock()
timeend = time.perf_counter()

totaltime = timeend - timestart

#print(room_img_res)
#print(batch_process)

if (not batch_process):
  room_img_res2 = Annotator.annotator(image, room_img_res)
else:
  room_img_res2 = []
  for x in room_img_res:
      #print(x)
      q = []
      for y in x:
          #print(y)
          q.append(y[0][0]) 
          q.append(y[0][1])
      #print(q)
      room_img_res2.append(q)


room_img_res2_area = []
for x in room_img_res_area:
  #print(x)
  q = []
  for y in x:
      #print(y)
      q.append(y[0][0]) 
      q.append(y[0][1])
  #print(q)
  room_img_res2_area.append(q)
  
room_img_res2_closest = []
for x in room_img_res_closest:
  #print(x)
  q = []
  for y in x:
      #print(y)
      q.append(y[0][0]) 
      q.append(y[0][1])
  #print(q)
  room_img_res2_closest.append(q)

print("Result")
#print(room_img_res2)

room_img_res3 = TextPostProcess.textPostProcess(image, room_img_res2, textlist)
room_img_res3_area = TextPostProcess.textPostProcess(image, room_img_res2_area, textlist)
room_img_res3_closest = TextPostProcess.textPostProcess(image, room_img_res2_closest, textlist)
#print(room_img_res3)


print(len(room_img_res2))
#print(len(room_img_res2))

if (saveBlacked):
    image1 = image.copy()
    (fh, ft) = os.path.splitext(image_file);
    blacked_filename = "black_" + fh + ".jpg"
    for x in room_img_res3:
        p = []
        for y in x[0]:
            p.append(y)
        #print(p)
        pts = np.array(p, np.int32) 
        pts = pts.reshape((-1,1,2))
        cv2.fillPoly(image1, [pts], (0, 0, 0))
    cv2.imwrite(blacked_filename, image1)

if (saveWhited):
    image1 = image.copy()
    (fh, ft) = os.path.splitext(image_file);
    whited_filename = "white_" + fh + ".jpg"
    for x in room_img_res3:
        p = []
        for y in x[0]:
            p.append(y)
        #print(p)
        pts = np.array(p, np.int32) 
        pts = pts.reshape((-1,1,2))
        cv2.fillPoly(image1, [pts], (255, 255, 255))
    cv2.imwrite(whited_filename, image1)


if (len(result_dir) > 0):
    if (not os.path.exists(result_dir)):
        #print(result_dir)
        os.mkdir(result_dir, 0o755)
    (fh, ft) = os.path.splitext(image_file);
    #print(fh)
    resfilename = result_dir + "/res_" + fh + "_room.txt"
    imgfilename = result_dir + "/img_" + fh + "_room.jpg"
    #print(resfilename)
    resfile = open(resfilename, "w", encoding='utf-8')
    resfile.write(str(len(room_img_res3)) + "\n")
    c1 = 0
    c2 = 100
    c3 = 200
    i = 1
    for x in room_img_res3:
        #print(x)
        #print(x[1])
        resfile.write(str(i) + " : ")
        a1 = calArea2(x[0])
        resfile.write(str(a1) + " : ")
        resfile.write(x[1] + " : ")
        for y in x[0]:
           #print(y)
           resfile.write(str(y) + " ")
        resfile.write("\n")
        p = []
        for y in x[0]:
            p.append(y)
        #print(p)
        pts = np.array(p, np.int32) 
        pts = pts.reshape((-1,1,2))
        #print(pts)
        avg = np.mean(pts, axis=0)
        avg1 = [int(x) for x in avg[0]]
        #print(avg)
        #print(avg1)
        cv2.fillPoly(image0, [pts], (c1, c2, c3))
        cv2.polylines(image0, [pts], True, (0,0,234), 3)
        cv2.putText(image0, str(i), (avg1[0], avg1[1]), cv2.FONT_ITALIC, 1.5, (255,255,255), thickness=7)
        c1 = (c1 + 29) % 203
        c2 = (c2 + 53) % 203
        c3 = (c3 + 97) % 203
        i = i+1
    resfile.write("Total time : " + str(totaltime))
    resfile.close()
    cv2.imwrite(imgfilename, image0)

    resfilename = result_dir + "/res_" + fh + "_area.txt"
    imgfilename = result_dir + "/img_" + fh + "_area.jpg"
    image0 = image.copy()
    #print(resfilename)
    resfile = open(resfilename, "w", encoding='utf-8')
    resfile.write(str(len(room_img_res3_area)) + "\n")
    c1 = 0
    c2 = 100
    c3 = 200
    i = 1
    for x in room_img_res3_area:
        #print(x)
        #print(x[1])
        resfile.write(str(i) + " : ")
        a1 = calArea2(x[0])
        resfile.write(str(a1) + " : ")
        resfile.write(x[1] + " : ")
        for y in x[0]:
           #print(y)
           resfile.write(str(y) + " ")
        resfile.write("\n")
        p = []
        for y in x[0]:
            p.append(y)
        #print(p)
        pts = np.array(p, np.int32) 
        pts = pts.reshape((-1,1,2))
        #print(pts)
        avg = np.mean(pts, axis=0)
        avg1 = [int(x) for x in avg[0]]
        #print(avg)
        #print(avg1)
        cv2.fillPoly(image0, [pts], (c1, c2, c3))
        cv2.polylines(image0, [pts], True, (0,0,234), 3)
        cv2.putText(image0, str(i), (avg1[0], avg1[1]), cv2.FONT_ITALIC, 1.5, (255,255,255), thickness=7)
        c1 = (c1 + 29) % 203
        c2 = (c2 + 53) % 203
        c3 = (c3 + 97) % 203
        i = i+1
    resfile.write("Total time : " + str(totaltime))
    resfile.close()
    cv2.imwrite(imgfilename, image0)

    resfilename = result_dir + "/res_" + fh + "_closest.txt"
    imgfilename = result_dir + "/img_" + fh + "_closest.jpg"
    image0 = image.copy()
    #print(resfilename)
    resfile = open(resfilename, "w", encoding='utf-8')
    resfile.write(str(len(room_img_res3_closest)) + "\n")
    c1 = 0
    c2 = 100
    c3 = 200
    i = 1
    for x in room_img_res3_closest:
        #print(x)
        #print(x[1])
        resfile.write(str(i) + " : ")
        a1 = calArea2(x[0])
        resfile.write(str(a1) + " : ")
        resfile.write(x[1] + " : ")
        for y in x[0]:
           #print(y)
           resfile.write(str(y) + " ")
        resfile.write("\n")
        p = []
        for y in x[0]:
            p.append(y)
        #print(p)
        pts = np.array(p, np.int32) 
        pts = pts.reshape((-1,1,2))
        #print(pts)
        avg = np.mean(pts, axis=0)
        avg1 = [int(x) for x in avg[0]]
        #print(avg)
        #print(avg1)
        cv2.fillPoly(image0, [pts], (c1, c2, c3))
        cv2.polylines(image0, [pts], True, (0,0,234), 3)
        cv2.putText(image0, str(i), (avg1[0], avg1[1]), cv2.FONT_ITALIC, 1.5, (255,255,255), thickness=7)
        c1 = (c1 + 29) % 203
        c2 = (c2 + 53) % 203
        c3 = (c3 + 97) % 203
        i = i+1
    resfile.write("Total time : " + str(totaltime))
    resfile.close()
    cv2.imwrite(imgfilename, image0)
