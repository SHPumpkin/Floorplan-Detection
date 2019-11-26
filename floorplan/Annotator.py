import cv2
from PIL import ImageTk
from PIL import Image as PILImage
import os
from tkinter import *
import tkinter as ttk
import numpy as np
import math
from shapely.geometry import Polygon, LineString



def annotator(image, room_img_res):

    c = 0
    annotator.drawable = 0
    annotator.mode = -1
    annotator.X = 0
    annotator.Y = 0
    annotator.lastDraw = 0
    annotator.cur_item= 0
    annotator.polyPoints = []
    annotator.combineIndex = []
    annotator.combineItemID = []
    annotator.buttonBaseColor = "000000"
    annotator.outlist = []
    input_value = ""
    entered_total_room_size = ""
    entered_width = ""
    entered_length = ""
    annotator.previous_button = -1
    index = -1


    def smooth(coordinates):
        #print("start smoothing")
        for t in range(0, len(coordinates) - 4, 2):
            threshold = 25
            if (coordinates[t] - coordinates[t+2]) * (coordinates[t] - coordinates[t+2]) + (coordinates[t+1] - coordinates[t+3]) * (coordinates[t+1] - coordinates[t+3]) <= threshold:
                coordinates[t + 1] = coordinates[t + 3]
                coordinates[t + 2] = coordinates[t]
                #print("smooth", coordinates[t], coordinates[t+1], coordinates[t+2], coordinates[t+3])
                # coordinates.pop(t+2)
                # coordinates.pop(t+3)
                # t = t - 2
        if (coordinates[0] - coordinates[len(coordinates) - 2]) * (coordinates[0] - coordinates[len(coordinates) - 2]) + (
                coordinates[1] - coordinates[len(coordinates) - 1]) * (
                coordinates[1] - coordinates[len(coordinates) - 1]) <= threshold:
            coordinates[0] = coordinates[len(coordinates) - 2]
            coordinates[len(coordinates) - 1] = coordinates[1]

        for t in range(len(coordinates) - 2, 4, -2):
            if coordinates[t] == coordinates[t-2] and coordinates[t-1] == coordinates[t-3]:
                coordinates.pop(t)
                coordinates.pop(t-1)

        if coordinates[0] == coordinates[len(coordinates) - 2] and coordinates[len(coordinates) - 1] == coordinates[1]:
            coordinates.pop(len(coordinates) - 1)
            coordinates.pop(len(coordinates) - 2)

        return coordinates

    def split_room():
        ##global annotator.mode, annotator.drawable, annotator.lastDraw
        if annotator.previous_button != 1 and annotator.previous_button != -1:
            clean_up_button_color(annotator.previous_button)
        annotator.previous_button = 1
        annotator.drawable = 0
        annotator.lastDraw = 0
        annotator.mode = 1
        annotator.split_button_1.config(bg="yellow")
        annotator.msg.config(text="Click on one end of the split line (has to be on a wall)")


    def split_room_horizontally():
        #global annotator.mode, annotator.drawable, annotator.lastDraw
        if annotator.previous_button != 4 and annotator.previous_button != -1:
            clean_up_button_color(annotator.previous_button)
        annotator.previous_button = 4
        annotator.drawable = 0
        annotator.lastDraw = 0
        annotator.mode = 4
        annotator.split_button_2.config(bg="yellow")
        annotator.msg.config(text="Click on one end of the split line (has to be on a wall)")


    def split_room_vertically():
        #global annotator.mode, annotator.drawable, annotator.lastDraw
        if annotator.previous_button != 5 and annotator.previous_button != -1:
            clean_up_button_color(annotator.previous_button)
        annotator.previous_button = 5
        annotator.drawable = 0
        annotator.lastDraw = 0
        annotator.mode = 5
        annotator.split_button_3.config(bg="yellow")
        annotator.msg.config(text="Click on one end of the split line (has to be on a wall)")


    def delete_room():
        #global annotator.mode, annotator.drawable, annotator.lastDraw
        if annotator.previous_button != 2 and annotator.previous_button != -1:
            clean_up_button_color(annotator.previous_button)
        annotator.previous_button = 2
        annotator.drawable = 0
        annotator.mode = 2
        annotator.delete_button.config(bg="yellow")
        annotator.msg.config(text="Click (anywhere) on the room you want to delete")


    def extend_wall():
        #global annotator.mode, annotator.drawable, annotator.lastDraw
        if annotator.previous_button != 6 and annotator.previous_button != -1:
            clean_up_button_color(annotator.previous_button)
        annotator.previous_button = 6
        annotator.drawable = 0
        annotator.lastDraw = 0
        annotator.mode = 6


    def draw_rect_room():
        #global annotator.mode, annotator.drawable, annotator.lastDraw
        if annotator.previous_button != 7 and annotator.previous_button != -1:
            clean_up_button_color(annotator.previous_button)
        annotator.previous_button = 7
        annotator.drawable = 0
        annotator.lastDraw = 0
        annotator.mode = 7
        annotator.draw_rect.config(bg="yellow")
        annotator.msg.config(text="Click on location of one corner of the rectangle")


    def draw_polygon_room():
        #global annotator.mode, annotator.drawable, annotator.lastDraw, annotator.polyPoints
        if annotator.previous_button != 8 and annotator.previous_button != -1:
            clean_up_button_color(annotator.previous_button)
        annotator.previous_button = 8
        annotator.drawable = 0
        annotator.lastDraw = 0
        annotator.mode = 8
        annotator.polyPoints = []
        annotator.draw_poly.config(bg="yellow")
        annotator.msg.config(text="Click on location of each point of the polygon in order")


    def combine_room():
        #global annotator.mode, annotator.drawable, annotator.lastDraw, annotator.combineIndex, annotator.combineItemID
        if annotator.previous_button != 9 and annotator.previous_button != -1:
            clean_up_button_color(annotator.previous_button)
        annotator.previous_button = 9
        annotator.drawable = 1
        annotator.lastDraw = 0
        annotator.mode = 9
        annotator.combineIndex = []
        annotator.combineItemID = []
        annotator.combine.config(bg="yellow")
        annotator.msg.config(text="Click on the first room to be combined")


    def end_draw_polygon_room():
        #global annotator.mode, annotator.drawable, annotator.lastDraw, annotator.polyPoints
        canvas.delete("TEMP")

        # check if polygon have intersection

        #print(annotator.polyPoints)
        newPoly = gen_Poly(annotator.polyPoints)
        #print(newPoly)
        #print(newPoly.area)
        objs = canvas.find_withtag("obj")
        #print(objs)
        intersect = False
        for obj in objs:
            coord = canvas.coords(obj)
            cPoly = gen_Poly(coord)
            #print(cPoly)
            intersect = newPoly.intersects(cPoly)
            if (intersect):
                break


        if (not intersect):
           poly = canvas.create_polygon(annotator.polyPoints, fill="#B0C4DE", outline='blue', width=5, tag="obj")
           annotator.msg.config(text="BUDAS")
        else:
           annotator.msg.config(text="New room cannot overlap with existing room")
        #canvas.tag_bind(poly, '<B1-Motion>', on_left_button_move)
        #canvas.tag_bind(poly, '<Button-1>', on_left_button_down)
        #canvas.tag_bind(poly, '<ButtonRelease-1>', on_left_button_up)
        #canvas.pack()
        annotator.polyPoints = []
        annotator.drawable = 0
        annotator.lastDraw = 0
        annotator.mode = -1
        annotator.draw_poly.config(bg=annotator.buttonBaseColor)


    def restore():
        #global annotator.mode, annotator.drawable, annotator.lastDraw
        if annotator.previous_button != 3 and annotator.previous_button != -1:
            clean_up_button_color(annotator.previous_button)
        annotator.previous_button = 3
        annotator.mode = 3
        annotator.drawable = 0
        annotator.lastDraw = 0
        canvas.delete("obj")
        # im = ImageTk.PhotoImage(image=PILImage.fromarray(image))
        # canvas.create_image(0, 0, image=im, anchor="nw")
        for p in room_img_res:
            l = []
            for q in p:
                for t in q:
                    l.append(t[0])
                    l.append(t[1])
            #print("l=", l)
            l1 = np.array(l, np.int32)
            #print("l1=", l1)
            poly = canvas.create_polygon(l, fill="#B0C4DE", outline='blue', width=5, tag="obj")
            #canvas.tag_bind(poly, '<B1-Motion>', on_left_button_move)
            #canvas.tag_bind(poly, '<Button-1>', on_left_button_down)
            #canvas.tag_bind(poly, '<ButtonRelease-1>', on_left_button_up)
        #canvas.pack()

    def save_to_file():
         outputfile = open("BUDAS_output.txt", "w")
         olist = canvas.find_withtag("obj")
         for x in olist:
             c = canvas.coords(x)
             c1 = [str(x) for x in c]
             outputfile.write(" ".join(c1))
             outputfile.write("\n\n")
         outputfile.close()

    def set_return_list():
        olist =  canvas.find_withtag("obj")
        for x in olist:
            c = canvas.coords(x)
            annotator.outlist.append(c)
        window.destroy()

    def clean_up_button_color(n):
        if  n == 1:
            annotator.split_button_1.config(bg=annotator.buttonBaseColor)
        elif n == 2:
            annotator.delete_button.config(bg=annotator.buttonBaseColor)
        elif n == 3:
            annotator.restore_button.config(bg=annotator.buttonBaseColor)
        elif n == 4:
            annotator.split_button_2.config(bg=annotator.buttonBaseColor)
        elif n == 5:
            annotator.split_button_3.config(bg=annotator.buttonBaseColor)
        elif n == 6:
            #EXTEND
            annotator.label_button.config(bg=annotator.buttonBaseColor)
        elif n == 7:
            annotator.draw_rect.config(bg=annotator.buttonBaseColor)
        elif n == 8:
            annotator.draw_poly.config(bg=annotator.buttonBaseColor)
        elif n == 9:
            annotator.combine.config(bg=annotator.buttonBaseColor)
        elif n == 10:
            annotator.label_button.config(bg=annotator.buttonBaseColor)
        elif n == 11:
            annotator.size_button.config(bg=annotator.buttonBaseColor)
        elif n == 12:
            annotator.draw_size_button.config(bg=annotator.buttonBaseColor)

    def is_drawable(event):
        return canvas.coords(event.widget.find_withtag("current")) == -1


    def on_left_button_down(event):
        #global annotator.X, annotator.Y, annotator.drawable, annotator.cur_item, annotator.mode, annotator.polyPoints, annotator.combineItemID, annotator.combineIndex
        cx = canvas.canvasx(event.x)
        cy = canvas.canvasy(event.y)
        #print("event : ", event.x, event.y, cx, cy)
        if annotator.mode == 3 or annotator.mode == -1:
            return
        if annotator.mode == 1 or annotator.mode == 4 or annotator.mode == 5 or annotator.mode == 13:
            annotator.msg.config(text="Drag mouse to the other end of the split line (has to be on a wall)")
            fixed_x, fixed_y, index = on_the_edge(cx, cy, canvas.coords(event.widget.find_withtag("current")))
            if index == -1:
                return
            annotator.X = fixed_x
            annotator.Y = fixed_y
            annotator.index = index
            annotator.cur_item = event.widget.find_withtag("current")
            annotator.drawable = 1
            return
        if annotator.mode == 12:
            annotator.msg.config(text="Drag mouse to draw a line)")
            annotator.X = cx
            annotator.Y = cy
            annotator.drawable = 1
            return
        if annotator.mode == 7:
            #print(is_drawable(event), canvas.coords(event.widget.find_withtag("current")))
            annotator.msg.config(text="Drag mouse to the opposite corner of the room")
            # if not is_drawable(event):
            #    return
            #print("7")
            annotator.X = cx
            annotator.Y = cy
            annotator.drawable = 1
            return
        if annotator.mode == 9:
            #print("9 down")
            l = find_Object(cx, cy)
            if (len(l) == 1):
                annotator.combineItemID.append(l[0])
                annotator.msg.config(text="Click on the second room to be combined")
            if (len(annotator.combineItemID) == 2):
               end_combine()

            '''
            fixed_x, fixed_y, index = on_the_edge(event.x, event.y, canvas.coords(event.widget.find_withtag("current")))
            if index == -1:
                return
            if len(annotator.combineItemID) < 2:
                annotator.combineItemID.append(event.widget.find_withtag("current"))

            coords = canvas.coords(event.widget.find_withtag("current"))
            x1 = coords[index]
            y1 = coords[index+1]
            if index + 3 < len(coords):
                x2 = coords[index+2]
                y2 = coords[index+3]
            else:
                x2 = coords[0]
                y2 = coords[1]
            if (x1 - fixed_x) * (x1 - fixed_x) + (y1 - fixed_y) * (y1 - fixed_y) > (x2 - fixed_x) * (x2 - fixed_x) + (y2 - fixed_y) * (y2 - fixed_y):
                index = index + 2
            annotator.combineIndex.append(index)
            canvas.create_oval(coords[index], coords[index+1], coords[index]+1, coords[index+1]+1, fill="blue", width=5, tag='TEMP')
            '''
            return

        if annotator.mode == 8:
            canvas.create_oval(cx, cy, cx+1, cy+1, fill="blue", width=5, tag='TEMP')
            annotator.polyPoints.append(cx)
            annotator.polyPoints.append(cy)

        annotator.drawable = 1
        #print("down:", cx, cy)
        annotator.X = cx
        annotator.Y = cy
        annotator.cur_item = event.widget.find_withtag("current")

    def on_left_button_move(event):
        #global annotator.lastDraw, annotator.X, annotator.Y, annotator.drawable, annotator.cur_item
        cx = canvas.canvasx(event.x)
        cy = canvas.canvasy(event.y)
        if annotator.drawable == 0 or (annotator.mode != 1 and annotator.mode != 4 and annotator.mode != 5 and annotator.mode != 7 and annotator.mode != 12 and annotator.mode != 13):
            return

        if annotator.mode == 7:
            # if not is_drawable(event):
            #   return
            try:
                canvas.delete(annotator.lastDraw)
            except Exception as e:
                pass
            annotator.lastDraw = canvas.create_polygon([annotator.X, annotator.Y, cx, annotator.Y, cx, cy, annotator.X, cy], fill="#B0C4DE", outline='blue', width=5, tag='TEMP')
            return

        item = event.widget.find_closest(cx, cy)[0]
        #print("item: ", event.widget.find_withtag("current"), annotator.cur_item, item)

        try:
            canvas.delete(annotator.lastDraw)
        except Exception as e:
            pass

        if annotator.mode == 4:
            annotator.lastDraw = canvas.create_line(annotator.X, annotator.Y, cx, annotator.Y, fill="blue", width=5, tag="TEMP")
        elif annotator.mode == 5:
            annotator.lastDraw = canvas.create_line(annotator.X, annotator.Y, annotator.X, cy, fill="blue", width=5, tag="TEMP")
        elif annotator.mode == 1 or annotator.mode == 12:
            annotator.lastDraw = canvas.create_line(annotator.X, annotator.Y, cx, cy, fill="blue", width=5, tag="TEMP")
        elif annotator.mode == 13:
            annotator.lastDraw = canvas.create_line(annotator.X, annotator.Y, cx, cy, fill="#FFA500", width=5, tag="TEMP")


    def on_left_button_up(event):
        global input_value
        #global annotator.X, annotator.Y, annotator.lastDraw, annotator.drawable, annotator.cur_item, annotator.mode, annotator.combineIndex, annotator.combineItemID
        cx = canvas.canvasx(event.x)
        cy = canvas.canvasy(event.y)
        #print("event : ", event.x, event.y, cx, cy)
        if annotator.mode == 8 or annotator.mode == -1:
            return

        # #print()
        if annotator.drawable == 0 or annotator.mode == 0:
            return
        #if annotator.mode == 7 and (not is_drawable(event)):
        #    return

        #if annotator.mode == 9:
            #print("9", len(annotator.combineIndex), annotator.combineIndex, annotator.combineItemID)
        if annotator.mode == 9 and len(annotator.combineIndex) == 4:
            end_combine()
            return

        draw_x = cx
        draw_y = cy
        if annotator.mode == 4:
            draw_y = annotator.Y

        if annotator.mode == 5:
            draw_x = annotator.X

        if annotator.mode == 12: #enter size by draw lines
            window2 = EnterDrawedLineLengthPopUp()
            window2.mainloop()
            annotator.msg.config(text="BUDAS")

            annotator.msg.config(text="No room clicked")
            annotator.mode = 0
            annotator.label_button.config(bg=annotator.buttonBaseColor)
            unit_length = float(input_value) / math.sqrt((cx - annotator.X)*(cx - annotator.X) + (cy - annotator.Y)*(cy - annotator.Y))
            try:
                canvas.delete(annotator.lastDraw)
            except Exception as e:
                pass
            print("unit length:" + str(unit_length) + " ft")


        if annotator.mode == 1 or annotator.mode == 4 or annotator.mode == 5 or annotator.mode == 13:  # split room
            if (annotator.mode == 1):
                annotator.split_button_1.config(bg=annotator.buttonBaseColor)
            elif (annotator.mode == 4):
                annotator.split_button_2.config(bg=annotator.buttonBaseColor)
            elif (annotator.mode == 5):
                annotator.split_button_3.config(bg=annotator.buttonBaseColor)
            elif (annotator.mode == 13):
                annotator.insert_door.config(bg=annotator.buttonBaseColor)
            _, _, first_index = on_the_edge(annotator.X, annotator.Y, canvas.coords(find_Object(annotator.X, annotator.Y)))
            fixed_x, fixed_y, index = on_the_edge(draw_x, draw_y, canvas.coords(find_Object(draw_x, draw_y)))
            if index == -1:
                annotator.drawable = 0
                canvas.delete(annotator.lastDraw)
                annotator.lastDraw = 0
                annotator.mode = 0
                annotator.msg.config(text="Endpoint do not touch wall. Split cancelled")
                return
            if annotator.mode == 13:
                if index != first_index:
                    annotator.drawable = 0
                    canvas.delete(annotator.lastDraw)
                    annotator.lastDraw = 0
                    annotator.mode = 0
                    annotator.msg.config(text="Endpoint do not touch the same wall. Draw door canceled")
                    return
                else:
                    annotator.drawable = 0
                    annotator.lastDraw = 0
                    annotator.msg.config(text="BUDAS")
                    return

            # canvas.create_line(annotator.X, annotator.Y, event.x, event.y, fill="blue", width=5)
            if first_index <= index:
                split_poly(annotator.cur_item, annotator.X, annotator.Y, fixed_x, fixed_y, first_index, index)
            else:
                split_poly(annotator.cur_item, fixed_x, fixed_y, annotator.X, annotator.Y, index, first_index)
            try:
                canvas.delete(annotator.lastDraw)
            except Exception as e:
                pass
            annotator.drawable = 0
            annotator.lastDraw = 0
            annotator.msg.config(text="BUDAS")

        elif annotator.mode == 7: # draw rectangle room
            annotator.draw_rect.config(bg=annotator.buttonBaseColor)
            l = find_Object(annotator.X, annotator.Y, cx, cy)
            canvas.delete("TEMP")
            if (len(l) == 0):
               poly_1 = canvas.create_polygon([annotator.X, annotator.Y, cx, annotator.Y, cx, cy, annotator.X, cy], fill="#B0C4DE", outline='blue', width=5, tag="obj")
               annotator.msg.config(text="BUDAS")
            else:
               annotator.msg.config(text="New room cannot overlap with existing room")
            annotator.mode = 0
            # poly_1 = canvas.create_rectangle(annotator.X, annotator.Y, event.x, event.y, fill="red", outline='blue', width=5, tag=['CLICK_LINE'])
            #canvas.tag_bind(poly_1, '<B1-Motion>', on_left_button_move)
            #canvas.tag_bind(poly_1, '<Button-1>', on_left_button_down)
            #canvas.tag_bind(poly_1, '<ButtonRelease-1>', on_left_button_up)

        elif annotator.mode == 2:  # delete room
            if (canvas.gettags(annotator.cur_item)[0] == "obj"):
               canvas.delete(annotator.cur_item)
               annotator.msg.config(text="BUDAS")
            else:
               annotator.msg.config(text="No room clicked")
            annotator.mode = 0
            annotator.delete_button.config(bg=annotator.buttonBaseColor)

        elif annotator.mode == 10:  # label room
            if (canvas.gettags(annotator.cur_item)[0] == "obj"):
                window2 = LabelInsertPopUp()
                window2.mainloop()
                label_selected_room(annotator.cur_item)
                annotator.msg.config(text="BUDAS")
            else:
                annotator.msg.config(text="No room clicked")
            annotator.mode = 0
            annotator.label_button.config(bg=annotator.buttonBaseColor)

        elif annotator.mode == 11: #room size
            if (canvas.gettags(annotator.cur_item)[0] == "obj"):
                window2 = RoomSizeInsertPopUp()
                window2.mainloop()
                size_of_selected_room(annotator.cur_item)
                annotator.msg.config(text="BUDAS")
            else:
                annotator.msg.config(text="No room clicked")
            annotator.mode = 0
            annotator.size_button.config(bg=annotator.buttonBaseColor)


        elif annotator.mode == 3:  # restore
            restore()
            annotator.msg.config(text="BUDAS")
            annotator.mode = 0

    def end_combine():
        #global annotator.drawable, annotator.cur_item, annotator.mode, annotator.combineIndex, annotator.combineItemID
        #print("here")
        '''
        canvas.delete("TEMP")
        coordinates1 = canvas.coords(annotator.combineItemID[0])
        coordinates2 = canvas.coords(annotator.combineItemID[1])
        back1 = False
        back2 = False
        #if annotator.combineIndex[0] > annotator.combineIndex[2]:
        #    tmp = annotator.combineIndex[0]
        #    annotator.combineIndex[0] = annotator.combineIndex[2]
        #    annotator.combineIndex[2] = tmp
        #    back1 = True
        #if annotator.combineIndex[1] > annotator.combineIndex[3]:
        #    tmp = annotator.combineIndex[1]
        #    annotator.combineIndex[1] = annotator.combineIndex[3]
        #    annotator.combineIndex[3] = tmp
        #    back2 = True
        coor1_1 = coordinates1[:annotator.combineIndex[2]+2]
        #print(annotator.combineIndex[0]+2, annotator.combineIndex[2], annotator.combineIndex[1], annotator.combineIndex[3]) # 18 - 20 0 - 2
        coor1_2 = coordinates1[0: annotator.combineIndex[0]+2]
        coor2_1 = coordinates2[annotator.combineIndex[1]:annotator.combineIndex[3]+2]
        coor2_2 = coordinates2[0:annotator.combineIndex[1]]
        coor2_3 = coordinates2[annotator.combineIndex[3]:]
        coor1_1.append(coor2_3)
        coor1_1.append(coor2_2)
        #coor1_1.append(coor1_2)
        '''
        coordinates1 = canvas.coords(annotator.combineItemID[0])
        coordinates2 = canvas.coords(annotator.combineItemID[1])
        poly1 = gen_Poly(coordinates1)
        poly2 = gen_Poly(coordinates2)
        if (poly1.overlaps(poly2)) or (poly1.touches(poly2)):
           p3 = poly1.union(poly2)
           if (p3.geom_type == "Polygon"):
               coord1_1 = list(p3.boundary.coords)
               canvas.delete(annotator.combineItemID[0])
               canvas.delete(annotator.combineItemID[1])
               poly_1 = canvas.create_polygon(coord1_1, fill="#B0C4DE", outline='blue', width=5, tag="obj")
               annotator.msg.config(text="BUDAS")
               annotator.combine.config(bg=annotator.buttonBaseColor)
               return
        p1 = poly1.boundary.coords
        p2 = poly2.boundary.coords
        l1 = []
        for i1 in range(0, len(p1)-1):
            l = LineString([p1[i1], p1[i1+1]])
            #print(l)
            l1.append(l)
        l2 = []
        for i2 in range(0, len(p2)-1):
            l = LineString([p2[i2], p2[i2+1]])
            #print(l)
            l2.append(l)
        minposx = -1
        minposy = -1
        mindist = 1000000.0
        for x in range(0,len(l1)):
            for y in range(0, len(l2)):
                if check_CanCombine(l1[x], l2[y]):
                    curdist = l1[x].distance(l2[y])
                    if (minposx == -1) or (curdist < mindist):
                        mindist = curdist
                        minposx = x
                        minposy = y
        if (mindist <= 10.0):
            x = minposx
            y = minposy
            #print(x, y)
            #print(coordinates1)
            #print(coordinates2)
            coord1_1 = coordinates1[0:2*(x+1)] + coordinates2[2*(y+1):] + coordinates2[0:2*(y+1)] + coordinates1[2*(x+1):]
            #print(coord1_1)
            #print(p1)
            #print(p2)
            canvas.delete(annotator.combineItemID[0])
            canvas.delete(annotator.combineItemID[1])
            poly_1 = canvas.create_polygon(coord1_1, fill="#B0C4DE", outline='blue', width=5, tag="obj")
            annotator.msg.config(text="BUDAS")
        else:
            annotator.msg.config(text="Rooms too far apart to be combined")
        #canvas.tag_bind(poly_1, '<B1-Motion>', on_left_button_move)
        #canvas.tag_bind(poly_1, '<Button-1>', on_left_button_down)
        #canvas.tag_bind(poly_1, '<ButtonRelease-1>', on_left_button_up)
        annotator.drawable = 0
        annotator.mode = -1
        annotator.combine.config(bg=annotator.buttonBaseColor)

    def split_poly(item, start_x, start_y, end_x, end_y, start_index, end_index):
        coordinates = canvas.coords(item)
        #print(item)
        #print(coordinates)
        ##print(coordinates, coordinates[len(coordinates)-1])
        #print(start_x, " ", start_y, " ", end_x, " ", end_y, " ", start_index, " ", end_index)
        coor1 = coordinates[:start_index + 2]
        coor2 = coordinates[start_index + 2:end_index + 2]
        coor3 = coordinates[end_index + 2:]
        #print("coor1:", len(coor1), coor1)
        #print("coor2:", len(coor2), coor2)
        #print("coor3:", len(coor3), coor3)
        #print("start:", start_x, start_y)
        #print("end", end_x, end_y)
        coor2.insert(0, start_x)
        coor2.insert(1, start_y)
        coor2.append(end_x)
        coor2.append(end_y)
        coor1.append(start_x)
        coor1.append(start_y)
        coor3.insert(0, end_x)
        coor3.insert(1, end_y)
        coor1 = coor1 + coor3
        #print("after coor1:", len(coor1), coor1)
        #print("after coor2:", len(coor2), coor2)
        canvas.delete(item)
        poly_1 = canvas.create_polygon(coor1, fill="#B0C4DE", outline='blue', width=5, tag="obj")
        #canvas.tag_bind(poly_1, '<B1-Motion>', on_left_button_move)
        #canvas.tag_bind(poly_1, '<Button-1>', on_left_button_down)
        #canvas.tag_bind(poly_1, '<ButtonRelease-1>', on_left_button_up)
        poly_2 = canvas.create_polygon(coor2, fill="#B0C4DE", outline='blue', width=5, tag="obj")
        #canvas.tag_bind(poly_2, '<B1-Motion>', on_left_button_move)
        #canvas.tag_bind(poly_2, '<Button-1>', on_left_button_down)
        #canvas.tag_bind(poly_2, '<ButtonRelease-1>', on_left_button_up)
        return

    def on_seg(px, py, x1, y1, x2, y2):
        #print("       on_seg: ", px, py, x1, y1, x2, y2)
        if (px - x1) * (y2 - y1) == (x2 - x1) * (py - y1) and min(x1, x2) <= px <= max(x1, x2) and min(y1, y2) <= py <= max(y1, y2):
            return True
        return False

    def find_center(coords):
        if len(coords) == 0:
            return 0, 0

        max_x = coords[0]
        min_x = coords[0]
        max_y = coords[1]
        min_y = coords[1]

        for i in range(0, len(coords)):
            if i % 2 == 0:
                max_x = max(max_x, coords[i])
                min_x = min(min_x, coords[i])
            else:
                max_y = max(max_y, coords[i])
                min_y = min(min_y, coords[i])
        return (max_x + min_x) / 2, (min_y + max_y) / 2

    def label_selected_room(item):
        global input_value
        coordinates = canvas.coords(item)
        tags = canvas.gettags(annotator.cur_item)
        if canvas.find_withtag("TAG4" + str(item[0])):
            print("delete existing label")
            canvas.delete(canvas.find_withtag("TAG4" + str(item[0])))
        print(tags)
        #if "labeled" in tags:
            #remove the previous tag
            #canvas.delete(canvas.find_withtag("TAG4"+str(item[0])))
        centerx, centery = find_center(coordinates)
        canvas.create_text(centerx, centery, text=input_value, tag="TAG4"+str(item[0]))
        print(item)
        #annotator.cur_item.tag_add("labeled")

    def enter_drawed_line_length(item):
        global input_value
        coordinates = canvas.coords(item)
        tags = canvas.gettags(annotator.cur_item)
        if canvas.find_withtag("TAG4" + str(item[0])):
            print("delete existing label")
            canvas.delete(canvas.find_withtag("TAG4" + str(item[0])))
        print(tags)
        #if "labeled" in tags:
            #remove the previous tag
            #canvas.delete(canvas.find_withtag("TAG4"+str(item[0])))
        centerx, centery = find_center(coordinates)
        canvas.create_text(centerx, centery, text=input_value, tag="TAG4"+str(item[0]))
        print(item)
        #annotator.cur_item.tag_add("labeled")

    def size_of_selected_room(item):
        global entered_total_room_size, entered_length, entered_width
        coordinates = canvas.coords(item)
        if canvas.find_withtag("SIZE4" + str(item[0])):
            print("delete existing size")
            canvas.delete(canvas.find_withtag("SIZE4" + str(item[0])))

        centerx, centery = find_center(coordinates)
        if len(entered_total_room_size) > 0:
            canvas.create_text(centerx, centery + 15, text=entered_total_room_size + " (ft^2)", tag="SIZE4"+str(item[0]))
        elif len(entered_length) > 0 and len(entered_width) > 0:
            canvas.create_text(centerx, centery + 15, text=entered_length + " (ft) * " + entered_width + " (ft)", tag="SIZE4" + str(item[0]))

    class EnterDrawedLineLengthPopUp(ttk.Toplevel):
        def __init__(self):
            super().__init__()
            self.title("line length")
            self.label_text = ""
            self.setupUI()

        def setupUI(self):
            row1 = ttk.Frame(self)
            row1.pack(fill="x")

            l = Label(row1, text="insert line length", height=2, width=10).pack(side=LEFT)

            self.label_text = StringVar()
            label = Entry(row1, textvariable=self.label_text).pack(side=RIGHT)
            row2 = ttk.Frame(self)
            row2.pack(fill="x")
            Button(row2, text="OK", command=self.on_click).pack(side=RIGHT)

        def on_click(self):
            global input_value
            input_value = self.label_text.get().lstrip()
            print("input: " + input_value)
            self.quit()
            self.destroy()


    class LabelInsertPopUp(ttk.Toplevel):
        def __init__(self):
            super().__init__()
            self.title("room label")
            self.label_text = ""
            self.setupUI()

        def setupUI(self):
            row1 = ttk.Frame(self)
            row1.pack(fill="x")

            l = Label(row1, text="insert label", height=2, width=10).pack(side=LEFT)

            self.label_text = StringVar()
            label = Entry(row1, textvariable=self.label_text).pack(side=RIGHT)
            row2 = ttk.Frame(self)
            row2.pack(fill="x")
            Button(row2, text="OK", command=self.on_click).pack(side=RIGHT)

        def on_click(self):
            global input_value
            input_value = self.label_text.get().lstrip()
            print("input: " + input_value)
            self.quit()
            self.destroy()

    class RoomSizeInsertPopUp(ttk.Toplevel):
        def __init__(self):
            super().__init__()
            self.title("room size(ft^2)")
            self.total_size_text = ""
            self.length = ""
            self.width = ""
            self.setupUI()

        def setupUI(self):
            v = IntVar()
            v.set(1)
            row1 = ttk.Frame(self)
            row1.pack(fill="x")
            Radiobutton(row1, text="totoal size(ft^2):", height=2, width=30, value=1, variable=v).pack(side=LEFT)
            self.total_size_text = StringVar()
            Entry(row1, textvariable=self.total_size_text).pack(side=RIGHT)

            row2 = ttk.Frame(self)
            row2.pack(fill="x")
            Radiobutton(row2, text="length(ft) * width(ft):", height=2, width=30, value=2, variable=v).pack(side=LEFT)
            self.length = StringVar()
            Entry(row2, textvariable=self.length).pack(side=RIGHT)

            row3 = ttk.Frame(self)
            row3.pack(fill="x")
            self.width = StringVar()
            Entry(row3, textvariable=self.width).pack(side=RIGHT)

            row4 = ttk.Frame(self)
            row4.pack(fill="x")
            Button(row4, text="OK", command=self.on_click).pack(side=RIGHT)

        def on_click(self):
            global entered_total_room_size, entered_length, entered_width
            entered_total_room_size = self.total_size_text.get().lstrip()
            entered_length = self.length.get().lstrip()
            entered_width = self.width.get().lstrip()
            print(entered_total_room_size, entered_length, entered_width)
            self.quit()
            self.destroy()

    def on_the_edge(px, py, coordinates):
        #print("On the edge : ", px, py, coordinates)
        dx = [0, 0, 0, 1, 1, 1, -1, -1, -1]
        dy = [0, 1, -1, 0, 1, -1, 0, 1, -1]
        if (len(coordinates) >= 4):
            for i in range(0, len(dx)):
                #print("  i : ", i)
                for t in range(0, len(coordinates) - 4, 2):
                    #print("    t : ", t)
                    found = on_seg(px + dx[i], py + dy[i], coordinates[t], coordinates[t+1], coordinates[t+2], coordinates[t+3])

                    if found:
                        return px + dx[i], py + dy[i], t
                found = on_seg(px + dx[i], py + dy[i], coordinates[0], coordinates[1], coordinates[len(coordinates)-2], coordinates[len(coordinates)-1])
                #print("            found : ", found)
                if found:
                    return px+dx[i], py+dy[i], len(coordinates) - 2
        return 0, 0, -1

    def find_Object(px, py, qx = -1, qy = -1):
        if (qx == -1):
           qx = px
        if (qy == -1):
           qy = py
        res = canvas.find_overlapping(px, py, qx, qy)
        sol = [x for x in res if canvas.gettags(x)[0] == "obj"]
        s0 = [canvas.gettags(x) for x in res]


        #print("find_Object : ", px, py, res, s0,  sol)
        return sol

    def gen_Poly(l):
        return(Polygon([(l[x], l[x+1]) for x in range(0, len(l), 2)]))

    def check_CanCombine(l1, l2):
        lp1 = list(l1.coords)
        lp2 = list(l2.coords)
        isvertical1 = (lp1[0][1] == lp1[1][1])
        isvertical2 = (lp2[0][1] == lp2[1][1])
        ishorizontal1 = (lp1[0][0] == lp1[1][0])
        ishorizontal2 = (lp2[0][0] == lp2[1][0])
        ##print(lp1, lp2)
        ##print(isvertical1, isvertical2, ishorizontal1, ishorizontal2)
        if (isvertical1):
            if (ishorizontal2):
                return False
            elif (isvertical2):
                return not ishorizontal1
            else:
                return True;
        elif (isvertical2):
            return not ishorizontal1
        else:
            isprepen = ((lp1[0][1] - lp1[1][1]) * (lp2[0][1] - lp2[1][1]) + (lp1[0][0] - lp1[1][0]) * (lp2[0][0] - lp2[1][0])) == 0
            ##print("isprepen : ", isprepen);
            if isprepen:
                return False
            else:
                issameslope = ((lp1[0][1] - lp1[1][1]) * (lp2[0][0] - lp2[1][0]) - (lp1[0][0] - lp1[1][0]) * (lp2[0][1] - lp2[1][1])) == 0
                if issameslope:
                   issameslope2 = ((lp1[0][1] - lp1[1][1]) * (lp2[0][0] - lp1[1][0]) - (lp1[0][0] - lp1[1][0]) * (lp2[0][1] - lp1[1][1])) == 0
                   if issameslope2:
                       if (lp1[0][0] < lp1[1][0]):
                          minx1 = lp1[0][0]
                          maxx1 = lp1[1][0]
                       else:
                          minx1 = lp1[1][0]
                          maxx1 = lp1[0][0]
                       if (lp2[0][0] < lp2[1][0]):
                          minx2 = lp2[0][0]
                          maxx2 = lp2[1][0]
                       else:
                          minx2 = lp2[1][0]
                          maxx2 = lp2[0][0]
                       return ((minx2 >= minx1) and (minx1 <= maxx2)) or ((minx1 >= minx2) and (minx1 <= maxx2))
                   else:
                      return True;
                   ##print("issameslpe, issamesploe2 ", issameslope, issameslope2)
                   return not issameslope2
                else:
                    return True

    def label_room():
        if annotator.previous_button != 10 and annotator.previous_button != -1:
            clean_up_button_color(annotator.previous_button)
        annotator.previous_button = 10
        annotator.drawable = 0
        annotator.mode = 10

        annotator.label_button.config(bg="yellow")
        annotator.msg.config(text="Click (anywhere) on the room you want to label")

    def room_size():
        if annotator.previous_button != 11 and annotator.previous_button != -1:
            clean_up_button_color(annotator.previous_button)
        annotator.previous_button = 11
        annotator.drawable = 0
        annotator.mode = 11
        annotator.size_button.config(bg="yellow")
        annotator.msg.config(text="Click (anywhere) on the room you want to enter the size")

    def draw_room_size():
        if annotator.previous_button != 12 and annotator.previous_button != -1:
            clean_up_button_color(annotator.previous_button)
        annotator.previous_button = 12
        annotator.drawable = 0
        annotator.mode = 12
        annotator.draw_size_button.config(bg="yellow")
        annotator.msg.config(text="Click (anywhere) on the room you want to enter the size by drawing a line")

    def draw_door():
        if annotator.previous_button != 13 and annotator.previous_button != -1:
            clean_up_button_color(annotator.previous_button)
        annotator.previous_button = 13
        annotator.drawable = 0
        annotator.mode = 13
        annotator.draw_door.config(bg="yellow")
        annotator.msg.config(text="Click on the wall where you want to insert a door")

    window = Tk()
    window.title("canvas window")
    #window.geometry('1024x1024')
    #f2 = Frame(window)

    #print("Image shape:")
    #print(image.shape[1])
    #print(image.shape[0])
    canvas = Canvas(window, width=1050, height=864, scrollregion=(0,0,image.shape[1], image.shape[0]))
    ##print("image 0:", image)
    im = ImageTk.PhotoImage(image=PILImage.fromarray(image))
    canvas.create_image(0, 0, image=im, anchor="nw", tag="image")
    ##print("image 1:", image)


    for p in room_img_res:
        l = []
        for q in p:
            for t in q:
                l.append(t[0])
                l.append(t[1])
        #print("l=", l)
        # l = smooth(l)
        l1 = np.array(l, np.int32)
        #print("l1=", l1)
        poly = canvas.create_polygon(l, fill="#B0C4DE", outline='blue', width=5, tag="obj")
        #canvas.tag_bind(poly, '<B1-Motion>', on_left_button_move)
        #canvas.tag_bind(poly, '<Button-1>', on_left_button_down)
        #canvas.tag_bind(poly, '<ButtonRelease-1>', on_left_button_up)

        c = c + 1
        # cv2.setMouseCallback('p'+'c', '<Button-1>', add_event)

    canvas.bind('<B1-Motion>', on_left_button_move)
    canvas.bind('<Button-1>', on_left_button_down)
    canvas.bind('<ButtonRelease-1>', on_left_button_up)


    annotator.split_button_1 = Button(window, text="Split Room", command=split_room)
    annotator.split_button_1.grid(column=0, row=0)
    annotator.buttonBaseColor = annotator.split_button_1.cget('background')
    annotator.split_button_2 = Button(window, text="Horizontally Split Room", command=split_room_horizontally)
    annotator.split_button_2.grid(column=1, row=0)
    annotator.split_button_3 = Button(window, text="Vertically Split Room", command=split_room_vertically)
    annotator.split_button_3.grid(column=2, row=0)
    annotator.draw_rect = Button(window, text="Draw Rectangle Room", command=draw_rect_room)
    annotator.draw_rect.grid(column=3, row=0)
    annotator.draw_poly = Button(window, text="Draw Polygon Room", command=draw_polygon_room)
    annotator.draw_poly.grid(column=4, row=0)
    annotator.end_draw_poly = Button(window, text="End Draw Polygon Room", command=end_draw_polygon_room)
    annotator.end_draw_poly.grid(column=5, row=0)
    annotator.combine = Button(window, text="Combine Room", command=combine_room)
    annotator.combine.grid(column=6, row=0)
    annotator.delete_button = Button(window, text="Delete", command=delete_room)
    annotator.delete_button.grid(column=7, row=0)
    annotator.restore_button = Button(window, text="Restore", command=restore)
    annotator.restore_button.grid(column=8, row=0)
    annotator.save_button = Button(window, text="Save", command=save_to_file)
    annotator.save_button.grid(column=9, row=0)
    annotator.label_button = Button(window, text="Label Room", command=label_room)
    annotator.label_button.grid(column=0, row=1)
    annotator.size_button = Button(window, text="Enter Size", command=room_size)
    annotator.size_button.grid(column=1, row=1)
    annotator.draw_size_button = Button(window, text="Draw Size", command=draw_room_size)
    annotator.draw_size_button.grid(column=2, row=1)
    annotator.insert_door = Button(window, text="Draw Door", command=draw_door)
    annotator.insert_door.grid(column=3, row=1)
    annotator.insert_door = Button(window, text="Draw Opening", command=draw_door)
    annotator.insert_door.grid(column=4, row=1)
    annotator.msg = Label(window, text="BUDAS")
    annotator.msg.grid(column=5, row=1, columnspan=5)

    '''
    split_button_1 = Button(window, text="Split Room", command=split_room).pack(padx=5, pady=10, side=LEFT)
    split_button_2 = Button(window, text="Horizontally Split Room", command=split_room_horizontally).pack(padx=5, pady=10, side=LEFT)
    split_button_3 = Button(window, text="Vertically Split Room", command=split_room_vertically).pack(padx=5, pady=10, side=LEFT)
    draw_rect = Button(window, text="Draw Rectangle Room", command=draw_rect_room).pack(padx=5, pady=10, side=LEFT)
    draw_poly = Button(window, text="Draw Polygon Room", command=draw_polygon_room).pack(padx=5, pady=10, side=LEFT)
    combine = Button(window, text="Combine Room", command=combine_room).pack(padx=5, pady=10, side=LEFT)
    end_draw_poly = Button(window, text="End Draw Polygon Room", command=end_draw_polygon_room).pack(padx=5, pady=10, side=LEFT)
    delete_button = Button(window, text="Delete", command=delete_room).pack(padx=5, pady=10, side=LEFT)
    restore_button = Button(window, text="Restore", command=restore).pack(padx=5, pady=10, side=LEFT)
    '''
    # split_combo_box = ttk.Combobox(window).pack()
    # split_combo_box['value'] = ('Horizontal Split', 'Vertical Split', 'Arbitrary Split')
    # extend_wall = Button(window, text="Extend Wall", command=extend_wall).pack(padx=5, pady=10, side=LEFT)



    #straight_line_only = Checkbutton(window, text="Straight Line").pack()

    #canvas.pack(expand=True, fill="both")
    #canvas.grid(column=0, row=3, columnspan=3)
    canvas.grid(column=0, row=2, columnspan=9)

    #window.pack(side=TOP, pady=10)
    if ((image.shape[1] > 864) or (image.shape[0] > 864)):
        hbar=Scrollbar(window,orient=HORIZONTAL)
        vbar=Scrollbar(window,orient=VERTICAL)
        hbar.grid(column=0, row=3, columnspan=9, sticky="ew")
        hbar.config(command=canvas.xview)
        vbar.grid(column=9, row=2, rowspan=2, sticky="ns")
        vbar.config(command=canvas.yview)
        canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
    window.protocol("WM_DELETE_WINDOW", set_return_list)

    window.mainloop()
    #print("finally : ")
    #return room_img_res
    return annotator.outlist






