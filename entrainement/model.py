import pickle

import numpy as np
from sklearn.utils import shuffle
from sklearn.svm import SVC



def getModel(clean_embed,clean_labels):
    """
        Cette fonstion permet d'enregistrer le model d'entrainement
        dans le fichier model.sav
    :param clean_embed: les vecteurs des images apres nettoyage
    :param clean_labels: les noms des images apres nettoyage
    :return: elle retourne un model de classification
    """
    print("[INFO] Wait to get model")
    try:
        embed_train, labels_train = shuffle(clean_embed, clean_labels)
        clf = SVC(C=10, gamma=0.001, kernel='rbf')
        clf.fit(np.squeeze(embed_train), labels_train)
        filename = 'model_test.sav'
        pickle.dump(clf, open(filename, 'wb'))
    except Exception as e:
        print(e)