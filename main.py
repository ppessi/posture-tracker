# -*- coding: utf-8 -*-
import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.config import Config
from kivy.core.window import Window

from functools import partial
import thread
import cv2
import os
import openface
import dlib
import sys
from scipy import misc
from PIL import Image

Window.clearcolor = (1,1,1,1)
Config.set('graphics','width','700')
Config.set('graphics','height','500')
Config.set('graphics','resizable',False)
# Config.set('graphics','minimum_width','700')
# Config.set('graphics','minimum_height','500')

class Data(Widget):
    text = ObjectProperty(None)
    img = ObjectProperty(None)
    faceRecognition = 0

    def __init__(self, faceRecognition):
        self.faceRecognition = faceRecognition
        super(Data,self).__init__()

    def update(self, dt):
        diff = self.faceRecognition.takeComparisonPicture()
        self.text.text = diff
        self.img.reload()

class FaceRecognition():
    boundingBox = None
    align = openface.AlignDlib("/home/pessi/webryhtikamera/openface/models/dlib/shape_predictor_68_face_landmarks.dat")

    def drawBoundingBox(self, img, boundingBox, color):
        if not boundingBox:
            return img
        width = len(img[0])
        height = len(img)
        left = max(0,boundingBox.left())
        right = min(width-1,boundingBox.right())
        top = max(0,boundingBox.top())
        bottom = min(height-1,boundingBox.bottom())
        square = []
        for y in range(max(0,top-1), min(bottom+1, width)):
            if left > 0:
                square.append([y,left-1])
            if right < width - 1:
                square.append([y,right+1])
            square.append([y,left+1])
            square.append([y,right-1])
            square.append([y,left])
            square.append([y,right])
        for x in range(max(0,left-1), min(right+1, width)):
            if top > 0:
                square.append([top-1,x])
            if bottom < height - 1:
                square.append([bottom+1,x])
            square.append([top+1,x])
            square.append([bottom-1,x])
            square.append([top,x])
            square.append([bottom,x])
        for pixel in square:
            img[pixel[0]][pixel[1]] = color
        return img

    def setRefPicture(self):
        img = self.takePicture()
        self.boundingBox = self.getBoundingBox(img)
        img = self.drawBoundingBox(img, self.boundingBox, (255,0,0))
        self.saveImg(img)

    def takeComparisonPicture(self):
        if not self.boundingBox:
            self.setRefPicture()
        img = self.takePicture()
        boundingBox = self.getBoundingBox(img)
        img = self.drawBoundingBox(img, self.boundingBox, (255,0,0))
        img = self.drawBoundingBox(img, boundingBox, (255, 255, 255))
        self.saveImg(img)
        if not boundingBox or not self.boundingBox:
            return "Face not found"
        diff_size = int(((boundingBox.area()-self.boundingBox.area())*1.0/self.boundingBox.area())*100)
#         diff_x = boundingBox.center().x-self.boundingBox.center().x
        # diff_y = boundingBox.center().y-self.boundingBox.center().y
        diff_x = int(((boundingBox.center().x-self.boundingBox.center().x)*1.0/self.boundingBox.width())*100)
        diff_y = int(((boundingBox.center().y-self.boundingBox.center().y)*1.0/self.boundingBox.height())*100)
        return "Relative difference in size: " + str(diff_size) + \
               "%\nRelative difference in location: " + str(diff_x) + "%, " + str(diff_y) + "%"

    def getBoundingBox(self, img):
        boundingBox = self.align.getLargestFaceBoundingBox(img)
        return boundingBox
       
    def takePicture(self):
        vc = cv2.VideoCapture(-1)
        rval, img = vc.read()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

    def saveImg(self, img):
        outimg = Image.fromarray(img, "RGB")
        outimg.save("1.png","PNG")
        

class MyApp(App):

    def build(self):
        faceRecognition = FaceRecognition()
        data = Data(faceRecognition)
        Clock.schedule_interval(data.update,0.1)
        return data

MyApp().run()
