import cv2
from PIL import ImageTk
from PIL import Image as PILImage
import os
from tkinter import *
import tkinter as ttk
import numpy as np
from shapely.geometry import Polygon, LineString



def textPostProcess(image, room_img_res, textlist):

    def gen_Poly(l):
        return(Polygon([(l[x], l[x+1]) for x in range(0, len(l), 2)]))

    def gen_Poly_From_Rect(l):
        return(Polygon([(l[0], l[1]), (l[2], l[1]), (l[2], l[3]), (l[0], l[3])]))


    textPostProcess.res = []
    listPoly = []
    for x in room_img_res:
        textPostProcess.res.append([x, ""])
        listPoly.append(gen_Poly(x))
    textPoly = []
    for x in textlist:
        textPoly.append(gen_Poly_From_Rect(x[1]))
    #print(listPoly)
    #print(textPoly)
    for i in range(0, len(room_img_res)):
        for j in range(0, len(textPoly)):
            if (listPoly[i].intersects(textPoly[j])):
                textPostProcess.res[i][1] = textPostProcess.res[i][1] + textlist[j][0]

    return textPostProcess.res

