"""
from multiprocessing import Process
import time
def loop_a():
    for i in range(3):
        time.sleep(2)
        print("a")

def loop_b():
    for i in range(3):
        print("b")
        time.sleep(2)

if __name__ == '__main__':
    Process(target=loop_a).start()
    Process(target=loop_b).start()

import multiprocessing
from random import randint

print(multiprocessing.cpu_count())


def generator_indx(list):
    indx = randint(1,21)
    while indx in list:
        indx = randint(1,21)
    print(indx)
    return indx

generator_indx([1,2,3,4,5,8,9,7])

"""
import cv2
import numpy
from PIL import Image
from mtcnn.mtcnn import MTCNN


def detection_face(image):
    # Create the haar cascade
    faceCascade = cv2.CascadeClassifier('C:/Users/allah/PycharmProjects/scraper_insta_google/haarcascade_frontalface_default.xml')

    # use numpy to convert the pil_image into a numpy array
    numpy_image1 = numpy.array(image)

    # convert to a openCV2 image, notice the COLOR_RGB2BGR which means that
    # the color is converted from RGB to BGR format
    img1 = cv2.cvtColor(numpy_image1, cv2.COLOR_RGB2BGR)

    # Read the image
    gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        #flags=cv2.cv.CV_HAAR_SCALE_IMAGE
    )
    if len(faces) == 1 :
        (x, y, w, h) = faces[0]
        face = img1[y:y + h, x:x + w]

        #convert cv2 to PIL image
        color_coverted = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(color_coverted)
        pil_image.show()

def detection_face_mtcnn(image):
    # use numpy to convert the pil_image into a numpy array
    numpy_image1 = numpy.array(image)

    # convert to a openCV2 image, notice the COLOR_RGB2BGR which means that
    # the color is converted from RGB to BGR format
    img1 = cv2.cvtColor(numpy_image1, cv2.COLOR_RGB2BGR)
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
    detector = MTCNN()
    faces = detector.detect_faces(img1)
    if len(faces) == 1 :
        (x, y, w, h) = faces[0]['box']
        face = img1[y:y + h, x:x + w]

        #convert cv2 to PIL image
        color_coverted = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(color_coverted)
        pil_image.show()

image = Image.open('a.jpg')
if detection_face_mtcnn(image) :
    print('coucou')

