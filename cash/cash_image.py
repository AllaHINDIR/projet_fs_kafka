import numpy
import numpy as np
import hashlib
import cv2
from skimage.metrics import structural_similarity as ssim


## methode with md5
def md5(image1,image2):
    """
    Cette fonction consiste à vérifier si deux image ont le meme hachage.
    :param image1: une image lu par PIL.Image.
    :param image2: une image lu par PIL.Image.
    :return: false si les deux images sont identiques.
    """
    try :
        f1_hash = hashlib.sha256(image1.tobytes()).hexdigest()
        f2_hash = hashlib.sha256(image2.tobytes()).hexdigest()

        if f1_hash == f2_hash:
            print("Both files are same")
            print(f"Hash: {f1_hash}")
            return False

        else:
            print("Files are different!")
            print(f"Hash of File 1: {f1_hash}")
            print(f"Hash of File 2: {f2_hash}")
            return True
    except Exception as ex :
        print('[ERROR] There is an exception : ', ex)


def mse(imageA, imageB):
    """
    Cette fonction consiste à calculer le MSE comme indice de similarité.
    :param imageA:une image lu par CV2.
    :param imageB:une image lu par CV2.
    :return: la valeur de l'indice (si il est proche de 0 alors les deux images sont plus similaires)
    """
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    return err
    # return the MSE, the lower the error, the more "similar"
    # the two images are

# methode Opencv
def open_cv(image1,image2):
    """
    Cette fonction consiste à caculer deux indice de similarité le MSE et SSIM.
    :param image1: une image lu par PIL.Image.
    :param image2: une image lu par PIL.Image.
    :return: en se basant sur les valeurs des deux indices la fonction retourne true si les 2 images ne sont pas similaire.
    """
    try :
        # use numpy to convert the pil_image into a numpy array
        numpy_image1 = numpy.array(image1)
        numpy_image2 = numpy.array(image2)

        # convert to a openCV2 image, notice the COLOR_RGB2BGR which means that
        # the color is converted from RGB to BGR format
        img1 = cv2.cvtColor(numpy_image1, cv2.COLOR_RGB2BGR)
        img2 = cv2.cvtColor(numpy_image2, cv2.COLOR_RGB2BGR)

        #img1 = cv2.imread(image1)
        #img2 = cv2.imread(image2)

        dim = (500,500)
        img1 = cv2.resize(img1,dim,interpolation=cv2.INTER_AREA)
        img2 = cv2.resize(img2,dim,interpolation=cv2.INTER_AREA)

        x1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        x2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)


        # cette methode compare les couleurs (B/R/V)
        diff = cv2.subtract(img1, img2)
        #print(diff)
        result = not np.any(diff)  # if diff is all zero it will return False


        m = mse(x1, x2)
        s = ssim(x1, x2)
        print ("mse: %s, ssim: %s" % (m, s))
        print(result)


        if s >= 0.8 and m < 2:
            print("Images are the same !")
            return False
        else:
            #cv2.imwrite('result.jpg', diff)
            print("The Images are different")
            return True
    except Exception as ex :
        print('[ERROR] There are an exception : ', ex)






