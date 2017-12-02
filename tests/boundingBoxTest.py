# This code takes pictures from a folder, recognizes the faces in them and colours the boundingBoxes black.
# Made for testing.

import openface
import cv2
import os
import sys
from scipy import misc
from PIL import Image

args = sys.argv

#args[1]: The path to the file 'shape_predictor_68_face_landmarks.dat' found in the openface/models/dlib folder.
align = openface.AlignDlib(args[1])

#args[2]: The path to a folder with pictures (of people)
path = args[2]

for file in os.listdir("output"):
    os.remove("output/" + file)

for file in os.listdir(path):
    a = raw_input("Press enter to continue, 0 and enter to quit: ")
    if a == "0":
        break
    image = misc.imread(path + "/" + file)
    print("File: " + file)
    boundingBoxes = align.getAllFaceBoundingBoxes(image)
    amount = len(boundingBoxes)
    if amount == 0:
        print("Didn't find any faces.")
    if amount == 1:
        print("Found 1 face.")
    else:
        print("Found " + str(amount) + " faces.")
    for i in range(len(boundingBoxes)):
        boundingBox = boundingBoxes[i]
        for y in range(boundingBox.top(), boundingBox.bottom()):
        	for x in range(boundingBox.left(), boundingBox.right()):
	            image[y][x] = (0,0,0)
    outimg = Image.fromarray(image, "RGB")
    outimg.save("output/" + file, "PNG")
    print("File saved in output.")
