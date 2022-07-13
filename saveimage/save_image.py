#If an image respect the resolution, it will be saved
import os
import random

import cv2
import numpy
import requests
import io
from PIL import Image
from cash import verification
import asyncio
import aiohttp
from storage import mongodb
from solr import solr

PATH = str(os.path.dirname(os.path.abspath('haarcascade_frontalface_default.xml')))
PATH = PATH + "\\saveimage\haarcascade_frontalface_default.xml"

def save_image( image_url, image_number,images_path,search_key,profession):
    """
        Cette fonction doit sauvegarder l'image dans Mongodb et FS
        après la vérification qu'elle n'existait pas...

    :param image_url: le lien de l'image
    :param image_number: le numéro de l'image
    :param images_path: le chemin dans lequel les images sont stockées
    :param search_key: le nom de la celebrité
    :param profession: le centre d'activité d la celebrité
    :return: True si l'image est bien stocké, sinon elle retourne False
    """

    try:
        print("[INFO] Image url:%s" % (image_url))
        search_string = ''.join(e for e in search_key if e.isalpha() or e.isspace())
        image = requests.get(image_url, timeout=10)
        if image.status_code == 200:
            with Image.open(io.BytesIO(image.content)) as image_from_web:
                try:
                    image_resolution = image_from_web.size
                    if image_resolution != None:
                        if detection_face(image_from_web) :
                            pil_image = detection_face(image_from_web)
                            if verification.NotExistInMongodb(image_url) is True:
                                filename = "%s%s.%s" % (search_string, str(image_number),image_from_web.format)
                                while not verification.NotExistInMongodbByFileName(filename):
                                    filename = "%s%s.%s" % (search_string, str(image_number)+str(random.randint(0,1000)), image_from_web.format)
                                mongodb.store_images(search_key,profession,filename,image_url)
                                print("[INFO] %d Image saved." % (image_number))
                                image_path = os.path.join(images_path, filename)
                                pil_image.save(image_path)
                                print("[INFO] %d Image saved at: %s" % (image_number, image_path))
                                pil_image.close()
                                #image_from_web.save(image_path)
                                image_from_web.close()
                                return True
                            else:
                                return False
                        else:
                            print('[ERROR] There are more than one face or zero face in this image')
                            return False
                    else:
                        print("[ERROR] The Image don't have a resolution !")
                        return False
                except OSError as oserror:
                    print("[ERREOR] Failed to be dowloaded", oserror)
                    return False
                image_from_web.close()
    except Exception as e:
        print("[ERREOR] Failed to be dowloaded", e)
        return False
    print("[INFO] Download Completed.")
    return True


def save_image_kafka( image_url, image_number,search_key,profession):
    """
        Cette fonction doit sauvegarder l'image dans Mongodb et Solr
        après la vérification qu'elle n'existait pas...
    :param image_url: le lien de l'image
    :param image_number: le numéro de l'image
    :param search_key: le nom de la celebrité
    :param profession: le centre d'activité d la celebrité
    :return: True si l'image est bien stocké, sinon elle retourne False
    """
    try:
        search_string = ''.join(e for e in search_key if e.isalpha() or e.isspace())
        image = requests.get(image_url, timeout=10)
        if image.status_code == 200:
            with Image.open(io.BytesIO(image.content)) as image_from_web:
                try:
                    image_resolution = image_from_web.size
                    if image_resolution != None:
                        if detection_face(image_from_web) :
                            pil_image = detection_face(image_from_web)
                            filename = "%s%s" % (search_string, str(image_number))
                            idImage = mongodb.store_images(search_key,profession, pil_image, filename, image_url,image_from_web.format)
                            solr.saveImageInSolr(idImage, image_url)
                            print("[INFO] %d Image saved." % (image_number))
                            image_from_web.close()
                            return True
                        else:
                            print('[ERROR] There are more than one face or zero face in this image')
                            return False
                    else:
                        print("[ERROR] The Image don't have a resolution !")
                        return False
                except OSError as oserror:
                    print("[ERREOR] Failed to be dowloaded", oserror)
                    return False
                image_from_web.close()
    except Exception as e:
        print("[ERREOR] Failed to be dowloaded", e)
        return False
    print("[INFO] Download Completed.")
    return True



def detection_face(image):
    """
            Cette fonction sert à la détection de visage dans une image
        en utilisant la methode haar cascade...puis, elle retourne le visage detecté.
    :param image: l'image qui va etre traitée
    :return: une image PIL qui n contint que le visage de la célébrité
    """
    # Create the haar cascade
    faceCascade = cv2.CascadeClassifier(PATH)

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
        minSize=(224, 224),
        #flags=cv2.cv.CV_HAAR_SCALE_IMAGE
    )
    if len(faces) == 1 :
        (x, y, w, h) = faces[0]
        face = img1[y:y + h, x:x + w]

        #convert cv2 to PIL image
        color_coverted = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(color_coverted)
        return pil_image


async def async_download_image(image_url, image_number,images_path,search_key):
    """
    Cette fonction permet de télécharger les images récupérer par le scrapeur en mode asynchrone.
    :param image_url: le lien de l'image.
    :param image_number: le numéro de l'image.
    :param images_path: le chemin de stockage des images.
    :param search_key: le nom de la célébrité concernée.
    :return:
    """
    try:
        print("[INFO] Image url:%s" % (image_url))
        search_string = ''.join(e for e in search_key if e.isalpha() or e.isspace())
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as res:
                if res.status == 200:
                    with Image.open(io.BytesIO(await res.content.read(n=-1))) as image_from_web:
                        try:
                            image_resolution = image_from_web.size
                            if image_resolution != None:
                                if verification.NotExist(search_key, image_from_web, image_url) is True:
                                    filename = "%s%s.jpeg" % (search_string, str(image_number))
                                    image_path = os.path.join(images_path, filename)
                                    print("[INFO] %d Image saved at: %s" % (image_number, image_path))
                                    image_from_web.save(image_path)
                                    # mongodb.store_images(search_key,image_from_web,image_url)
                                    image_from_web.close()
                                else:
                                    return False
                            else:
                                print("[ERROR] The Image don't have a resolution !")
                                return False
                        except OSError:
                            rgb_im = image_from_web.convert('RGB')
                            rgb_im.save(image_path)
                        image_from_web.close()
    except Exception as e:
        print("[ERREOR] Failed to be dowloaded", e)
        return False
    print("[INFO] Download Completed.")
    return True

