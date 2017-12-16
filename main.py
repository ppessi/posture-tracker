# -*- coding: utf-8 -*-
import kivy
kivy.require('1.9.0')

from kivy.config import Config
Config.set('graphics','width','700')
Config.set('graphics','height','500')
Config.set('graphics','resizable',False)

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.lang import Builder

from functools import partial
import thread
import cv2
import os
import openface
import dlib
import sys
import numpy as np
from scipy import misc
from PIL import Image

Window.clearcolor = (1,1,1,1)
Builder.load_file('gui.kv')

class TakePhoto(Screen):
    image = ObjectProperty(None)
    button = ObjectProperty(None)
    buttonColors = [(0.9,0.9,0.9,1), (0.9,0.9,0.9,0.5)]

    picture = None 
    takingPictures = False
    events = []
    faceRec = None
    bBox = None

    def __init__(self, **kwargs):
        super(TakePhoto,self).__init__(**kwargs)
        self.faceRec = FaceRecognition()

    def update(self, dt):
        if self.picture == None:
            return
        boundingBox = self.faceRec.getBoundingBox(self.picture)
        self.button.disabled = not boundingBox
        self.button.background_color = self.buttonColors[not boundingBox]
        img = self.faceRec.drawBoundingBox(self.picture, boundingBox, (255,0,0))
        for i in range(len(img)):
            img[i] = img[i][::-1]
        outimg = Image.fromarray(img, "RGB")
        outimg.save("1.png","PNG")
        self.image.reload()

    def on_touch_down(self, touch):
        if self.button.collide_point(*touch.pos):
            thread.start_new_thread(self.setRef,())
            return True
        return super(TakePhoto,self).on_touch_down(touch)

    def on_enter(self):
        self.takingPictures = True
        rval, img = cv2.VideoCapture(-1).read()
        img = np.zeros((len(img),len(img[0]),3),dtype=np.uint8)
        outimg = Image.fromarray(img, "RGB")
        outimg.save("1.png","PNG")
        self.image.reload()
        self.image.color = 1,1,1,1
        thread.start_new_thread(self.takePictures,()) 
        self.events.append(Clock.schedule_interval(self.update,0.1))

    def on_pre_leave(self):
        self.takingPictures = False
        for event in self.events:
            event.cancel()
        self.events = []

    def takePictures(self):
        vc = cv2.VideoCapture(-1)
       
        while self.takingPictures:
            rval, img = vc.read()
            if not rval:
                continue
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.picture = img

    def setRef(self):
        global refBBox
        refBBox = None
        while not refBBox:
            refBBox = self.faceRec.getBoundingBox(self.picture)
        self.manager.current = 'trackPosture'

class PostureTracking(Screen):
    image = ObjectProperty(None)

    refBBox = None
    events = []
    faceRec = None
    colors = [(1,0,0,1),(0,1,0,1)]
    gray = (0.5,0.5,0.5,1)

    def on_enter(self):
        global refBBox
        self.refBBox = refBBox
        self.faceRec = FaceRecognition()
        self.events.append(Clock.schedule_interval(self.update,0.1))

    def on_pre_leave(self):
        for event in self.events:
            event.cancel()
        self.events = []

    def update(self,dt):
        vc = cv2.VideoCapture(-1)
        rval, img = vc.read()
        if not rval:
            print("Could not take picture")
            return
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        bBox = self.faceRec.getBoundingBox(img)
        diff = self.faceRec.compareFacePosition(bBox, self.refBBox)
        self.image.color = 1,1,1,1
        if not bBox: #face not found
            self.image.source = "textures/6.png"
        elif (diff[0] < -30): #leaned backwards
            self.image.source = "textures/4.png"
        elif (diff[0] > 40): #leaned forwards
            self.image.source = "textures/2.png"
        elif (abs(diff[1]) > 50): #leaning to the side 
            self.image.source = "textures/6.png"
            self.image.color = 1,0,0,1
        elif (diff[2]) > 20: #slouch
            self.image.source = "textures/3.png"
        elif (diff[2]) < -20: #somehow much higher than normal position
            self.image.source = "textures/5.png"
        else: #good posture
            self.image.source = "textures/1.png"
        self.image.reload()

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
        if not bBox1 or not bBox2:
            return None
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
       
sm = ScreenManager(transition=NoTransition())
sm.add_widget(TakePhoto(name='takePhoto'))
sm.add_widget(PostureTracking(name='trackPosture'))

refBBox = None

class PostureTrackerApp(App):

    def build(self):
        return sm

PostureTrackerApp().run()
