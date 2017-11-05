import openface
import numpy
import dlib
import cv2
import os
from scipy import misc
from PIL import Image

align = openface.AlignDlib("/home/pessi/webryhtikamera/openface/models/dlib/shape_predictor_68_face_landmarks.dat")
path = "/home/pessi/Pictures/Webcam/kumartunut"
for file in os.listdir(path):
    #image = cv2.imread(path + "/" + file)
    image = misc.imread(path + "/" + file)
    boundingBoxes = align.getAllFaceBoundingBoxes(image)
    for i in range(len(boundingBoxes)):
        boundingBox = boundingBoxes[i]
        for y in range(boundingBox.top(), boundingBox.bottom()):
        	for x in range(boundingBox.left(), boundingBox.right()):
	            image[y][x] = (0,0,0)
    outimg = Image.fromarray(image, "RGB")
    outimg.save("output/" + file, "PNG")
    print(file)
