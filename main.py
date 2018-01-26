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
import time
from scipy import misc
from PIL import Image

import notify

Window.clearcolor = (1,1,1,1)
Builder.load_file('gui.kv')

class Settings(Screen):
    timeButton = ObjectProperty(None)
    continueButton = ObjectProperty(None)
    dropDown = ObjectProperty(None)
    checkBox = ObjectProperty(None)

    notificationInterval = 5
    next = 'takePhoto'

    def __init__(self, **kwargs):
        super(Settings, self).__init__(**kwargs)
        self.timeButton.bind(on_release=self.dropDown.open)

    def setTime(self, time):
        self.notificationInterval = int(time)
        self.timeButton.text = time

    def on_touch_down(self, touch):
        if self.continueButton.collide_point(*touch.pos):
            self.manager.current = self.next
            self.next = 'trackPosture'
            return True
        return super(Settings,self).on_touch_down(touch)

    def on_leave(self):
        global notificationInterval, checkSidewaysMovement
        notificationInterval = self.notificationInterval
        checkSidewaysMovement = self.checkBox.active

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
        self.image.color = (1,1,1,1)

    def on_touch_down(self, touch):
        if self.button.collide_point(*touch.pos):
            thread.start_new_thread(self.setRef,())
            return True
        return super(TakePhoto,self).on_touch_down(touch)

    def on_enter(self):
        self.takingPictures = True
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

        rval, img = vc.read()
        img = np.zeros((len(img),len(img[0]),3),dtype=np.uint8)
        outimg = Image.fromarray(img, "RGB")
        outimg.save("1.png","PNG")

    def setRef(self):
        global refBBox 
        refBBox = None
        while not refBBox:
            refBBox = self.faceRec.getBoundingBox(self.picture)
        self.manager.current = 'trackPosture'

class PostureTracking(Screen):
    image = ObjectProperty(None)
    settingButton = ObjectProperty(None)
    photoButton = ObjectProperty(None)

    refBBox = None
    notificationInterval = 0
    checkSidewaysMovement = 0
    events = []
    faceRec = None
    colors = [(1,0,0,1),(0,1,0,1)]
    gray = (0.5,0.5,0.5,1)
    multiplier = 1

    badPositionCount = 0
    badPictureCount = 0

    def on_enter(self):
        global refBBox, notificationInterval, checkSidewaysMovement
        self.refBBox = refBBox
        self.notificationInterval = notificationInterval
        self.checkSidewaysMovement = checkSidewaysMovement
        self.faceRec = FaceRecognition()
        self.badPictureCount = 0
        self.badPositionCount = 0
        self.events.append(Clock.schedule_interval(self.update,60))

    def on_pre_leave(self):
        for event in self.events:
            event.cancel()
        self.events = []

    def on_touch_down(self, touch):
        if self.settingButton.collide_point(*touch.pos):
            self.manager.current = 'settings'            
            return True
        elif self.photoButton.collide_point(*touch.pos):
            self.manager.current = 'takePhoto'
            return True
        return super(PostureTracking,self).on_touch_down(touch)

    def update(self,dt):
        vc = cv2.VideoCapture(-1)
        rval, img = vc.read()
        if not rval:
            notify.send("Posture Tracker", "Webcam is not working")
            return
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        bBox = self.faceRec.getBoundingBox(img)
        diff = self.faceRec.compareFacePosition(bBox, self.refBBox)
        self.image.color = 1,1,1,1
        if bBox: #face found
            self.badPictureCount = 0
            self.badPositionCount += 1
            #leaned backwards
            if diff[0] < -30 or diff[2] > 20:
                self.image.source = "textures/leanedback.png"
            #leaned forwards
            elif diff[0] > 40:
                self.image.source = "textures/crouch.png"
            #leaning to the side, only checked when checkSidewaysMovements is true
            elif self.checkSidewaysMovement and abs(diff[1]) > 50:
                self.image.source = "textures/side.png"
                self.image.color = 1,0,0,1
            #higher than normal position
            elif diff[2] < -20:
                self.image.source = "textures/high.png"
            #good posture
            else:
                self.image.source = "textures/good.png"
                self.badPositionCount = 0
                self.multiplier = 1
        #face not found
        else:
            self.image.source = "textures/notfound.png"
            self.badPictureCount += 1

        self.image.reload()
        
        if self.badPictureCount > min(10,self.notificationInterval):
            notify.send("Posture Tracker", "I can't see you! Are you still there? Brighter lighting might be necessary")
        elif self.badPositionCount == self.notificationInterval * self.multiplier:
            notify.send("Posture Tracker", "You have been sitting badly for " + str(self.badPositionCount) + " minutes")
        elif self.badPositionCount > self.notificationInterval * self.multiplier:
            notify.send("Posture Tracker", "It seems you're still sitting badly. Or maybe you should take a new reference picture?")
            self.multiplier += 1

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
sm.add_widget(Settings(name='settings'))
sm.add_widget(TakePhoto(name='takePhoto'))
sm.add_widget(PostureTracking(name='trackPosture'))

refBBox = None
notificationInterval = 5 * 60
checkSidewaysMovement = False

class PostureTrackerApp(App):

    def build(self):
        notify.init("Posture Tracker")
        return sm

PostureTrackerApp().run()
