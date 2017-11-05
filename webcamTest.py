# -*- coding: utf-8 -*-

"""
Takes pictures with a webcam and saves them. Made for testing.
"""

import cv2
from PIL import Image

vc = cv2.VideoCapture(-1)

i = 0
print("Press enter to take pictures, 0 and enter quits the program.")
while True:
    i+=1
    a = raw_input()
    if a == "0":
        break
    print("Picture taken.")
    rval, frame = vc.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    outimg = Image.fromarray(frame, "RGB")
    outimg.save("output/" + str(i) + ".png", "PNG")

