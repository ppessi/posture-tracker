# -*- coding: utf-8 -*-

import cv2
from PIL import Image

vc = cv2.VideoCapture(-1)

i = 0
print("Paina enteriä ottaaksesi kuvia, 0 lopettaa.")
while True:
    i+=1
    a = raw_input()
    if a == "0":
        break
    print("Kuva otettu.")
    rval, frame = vc.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    outimg = Image.fromarray(frame, "RGB")
    outimg.save("output/" + str(i) + ".png", "PNG")

