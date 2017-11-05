# -*- coding: utf-8 -*-

import thread
import cv2
import os
import openface
import numpy
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
    raw_input("Ensin otetaan vertailukuva. Paina enteriä kun olet valmis.")
    while True:
        img = pictures[0]
        bBox = align.getLargestFaceBoundingBox(img)
        if bBox != None:
            break
    print("Kuva otettu.")
    leveys = len(img[0])
    korkeus = len(img)
    origLeft = max(0,bBox.left())
    origRight = min(leveys-1,bBox.right())
    origTop = max(0,bBox.top())
    origBottom = min(korkeus-1,bBox.bottom())
    red = (255, 0, 0)
    for y in range(origTop, origBottom):
        img[y][origLeft] = red
        img[y][origRight] = red
    for x in range(origLeft, origRight):
        img[origTop][x] = red
        img[origBottom][x] = red
    outimg = Image.fromarray(img, "RGB")
    outimg.save("output/00.png", "PNG")
    print("Kuva tallennettu.")
    print
    print("Paina enteriä ottaaksesi kuvia, 0 lopettaa.")
    while True:
        i+=1
        a = raw_input()
        if a == "0":
            break
        img = pictures[0]
        print("Kuva otettu.")

        bBox = align.getLargestFaceBoundingBox(img)
        if bBox == None:
            print("Kasvoja ei löydetty.")
            continue
        left = max(0,bBox.left())
        right = min(leveys-1,bBox.right())
        top = max(0,bBox.top())
        bottom = min(korkeus-1,bBox.bottom())
        black = (0,0,0)
        red = (255, 0, 0)
        print("Erot sijainnissa:")
        print("  Muutos pystysuunnassa (yläreuna): " + str(origTop - top))
        print("  Muutos pystysuunnassa (alareuna): " + str(origBottom - bottom))
        print("  Muutos sivusuunnassa (vasen reuna): " + str(left - origLeft))
        print("  Muutos sivusuunnassa (oikea reuna): " + str(right - origRight))
        for y in range(origTop, origBottom):
            img[y][origLeft] = red
            img[y][origRight] = red
        for x in range(origLeft, origRight):
            img[origTop][x] = red
            img[origBottom][x] = red
        for y in range(top, bottom):
            img[y][left] = black
            img[y][right] = black
        for x in range(left, right):
            img[top][x] = black
            img[bottom][x] = black
        outimg = Image.fromarray(img, "RGB")
        outimg.save("output/" + "0" * (2 - len(str(i))) + str(i) + ".png", "PNG")
        print("Kuva tallennettu.")
    sys.exit()

main()
