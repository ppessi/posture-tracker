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

class Data(Widget):
    text = ObjectProperty(None)
    img = ObjectProperty(None)
    button = ObjectProperty(None)
    faceRecognition = 0

    def __init__(self, faceRecognition):
        self.faceRecognition = faceRecognition
        super(Data,self).__init__()

    def update(self, dt):
        diff = self.faceRecognition.takeComparisonPicture()
        self.text.text = diff
        self.img.reload()

    def on_touch_down(self, touch):
        if self.button.collide_point(*touch.pos):
            Clock.schedule_interval(lambda dt: self.faceRecognition.setRefPicture(), 0.1)
            return True
        return super(Data,self).on_touch_down(touch)

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
        if self.boundingBox != None:
            return False

    def takeComparisonPicture(self):
        if not self.boundingBox:
            self.setRefPicture()
            return "Face not found"
        img = self.takePicture()
        boundingBox = self.getBoundingBox(img)
        img = self.drawBoundingBox(img, self.boundingBox, (255,0,0))
        img = self.drawBoundingBox(img, boundingBox, (255,255,255))
        self.saveImg(img)
        if not boundingBox or not self.boundingBox:
            return "Face not found"
        diff = self.compareFacePosition(boundingBox, self.boundingBox)
        return "Relative difference in size: " + str(diff[0]) + \
               "%\nRelative difference in location: " + str(diff[1]) + "%, " + str(diff[2]) + "%"

    def compareFacePosition(self, bBox1, bBox2):
        diff_size = int(((bBox1.area()-bBox2.area())*1.0/bBox2.area())*100)
        diff_x = int(((bBox1.center().x-bBox2.center().x)*1.0/bBox2.width())*100)
        diff_y = int(((bBox1.center().y-bBox2.center().y)*1.0/bBox2.height())*100)
        return [diff_size, diff_x, diff_y]

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
        

class TestApp(App):

    def build(self):
        faceRecognition = FaceRecognition()
        data = Data(faceRecognition)
        Clock.schedule_interval(lambda dt: faceRecognition.setRefPicture(), 0.1)
        Clock.schedule_interval(data.update,2)
        return data

TestApp().run()
