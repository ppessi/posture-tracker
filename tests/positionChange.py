# -*- coding: utf-8 -*-

"""
This code takes pictures with the webcam and recognizes the faces in them.
First it takes a picture to which it compares the other pictures.
It draws a red frame around the largest face in the first picture.
It then draws the red frame in all other pictures, and also draws black frames around the largest faces in the other pictures.
Meant for testing, to see how much the head's positions changes in different postures.
"""

import thread
import cv2
import os
import openface
import dlib
import sys
from scipy import misc
from PIL import Image

def takePictures(pictures):
    vc = cv2.VideoCapture(-1)
    while len(pictures) < 3:
        rval, picture = vc.read()
        picture = cv2.cvtColor(picture, cv2.COLOR_BGR2RGB)
        pictures.append(picture)
    while True:
        rval, picture = vc.read()
        picture = cv2.cvtColor(picture, cv2.COLOR_BGR2RGB)
        pictures.append(picture)
        pictures.pop(0)

def main():
    pictures = []
    
    thread.start_new_thread(takePictures, (pictures,))

    path = "output"
    for file in os.listdir(path):
        os.remove(path + "/" + file)

    align = openface.AlignDlib("/home/pessi/webryhtikamera/openface/models/dlib/shape_predictor_68_face_landmarks.dat")

    i = 0
    while len(pictures) == 0:
        continue
    raw_input("First the program will take a picture that will be used for comparison. Press enter when you're ready.")
    while True:
        img = pictures[0]
        bBox = align.getLargestFaceBoundingBox(img)
        if bBox != None:
            break
        print("Face not recognized, taking another picture.")
    print("Picture taken.")
    width = len(img[0])
    height = len(img)
    origLeft = max(0,bBox.left())
    origRight = min(width-1,bBox.right())
    origTop = max(0,bBox.top())
    origBottom = min(height-1,bBox.bottom())
    red = (255, 0, 0)
    redSquare = []
    for y in range(max(0,origTop-1), min(origBottom+1, width)):
        if origLeft > 0:
            redSquare.append([y,origLeft-1])
        if origRight < width - 1:
            redSquare.append([y,origRight+1])
        redSquare.append([y,origLeft+1])
        redSquare.append([y,origRight-1])
        redSquare.append([y,origLeft])
        redSquare.append([y,origRight])
    for x in range(max(0,origLeft-1), min(origRight+1, width)):
        if origTop > 0:
            redSquare.append([origTop-1,x])
        if origBottom < height - 1:
            redSquare.append([origBottom+1,x])
        redSquare.append([origTop+1,x])
        redSquare.append([origBottom-1,x])
        redSquare.append([origTop,x])
        redSquare.append([origBottom,x])
    for pixel in redSquare:
        img[pixel[0]][pixel[1]] = red
    outimg = Image.fromarray(img, "RGB")
    outimg.save("output/00.png", "PNG")
    print("Picture saved into output.")
    print
    print("Press enter to take a picture, 0 and enter will quit the program.")
    while True:
        i+=1
        a = raw_input()
        if a == "0":
            break
        img = pictures[0]
        print("Picture taken.")

        bBox = align.getLargestFaceBoundingBox(img)
        if bBox == None:
            print("No faces found.")
            continue
        
        left = max(0,bBox.left())
        right = min(width-1,bBox.right())
        top = max(0,bBox.top())
        bottom = min(height-1,bBox.bottom())
        black = (0,0,0)
        red = (255, 0, 0)

        print("Differences in position:")
        print("  Change in vertical direction (upper border): " + str(origTop - top))
        print("  Change in vertical direction (lower border): " + str(origBottom - bottom))
        print("  Change in horizontal direction (left border): " + str(left - origLeft))
        print("  Change in horizontal direction (left border): " + str(right - origRight))
        
        for pixel in redSquare:
            img[pixel[0]][pixel[1]] = red
        for y in range(max(0,top-1), min(bottom+1,height-1)):
            if left > 0:
                img[y][left-1] = black
            if right < width-1:
                img[y][right+1] = black
            img[y][left+1] = black
            img[y][right-1] = black
            img[y][left] = black
            img[y][right] = black
        for x in range(left, right):
            if top > 0:
                img[top-1][x] = black
            if bottom < height-1:
                img[bottom+1][x] = black
            img[top+1][x] = black
            img[bottom-1][x] = black
            img[top][x] = black
            img[bottom][x] = black

        outimg = Image.fromarray(img, "RGB")
        outimg.save("output/" + "0" * (2 - len(str(i))) + str(i) + ".png", "PNG")
        print("Picture saved into output.")
    sys.exit()

main()
