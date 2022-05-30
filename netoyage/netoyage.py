import os
from collections import defaultdict
from os import listdir
import cv2
import numpy as np


from entrainement.message import InceptionResNetV2
from storage import connexion
from storage import celebrity_schema
from numpy.linalg import norm


PATH = str(os.path.dirname(os.path.abspath('netoyage.py')))
PATH = PATH.removesuffix('netoyage')
PATH_FACENET = PATH + '\\facenet_keras_weights.h5'
PATH_PHOTOS = PATH + '\\photos'


def get_embedding(model,image):
    samples = np.expand_dims(image, axis=0)
    yhat = model.predict(samples)
    embedding = yhat[0]
    return embedding

def get_data(dataset_path,model):
    images = []
    labels = []
    names = []
    embeddings = []
    try:

        for dire in listdir(dataset_path):
            for f in listdir(dataset_path+'/'+dire):
                if "jpeg" in f or "JPEG" in f or "png" in f or "PNG" in f or "jpg" in f or "JPG" in f:
                    image_path = dataset_path + '/' + dire + '/' + f
                    #image = cv2.imread(image_path)
                    image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8),cv2.IMREAD_UNCHANGED)
                    image = np.asarray(image, dtype=np.float32)
                    image = cv2.resize(image, (224, 224), interpolation = cv2.INTER_AREA)
                    image = cv2.resize(image, (160, 160))
                    image = image.astype('float32')
                    mean, std = image.mean(), image.std()
                    image = (image - mean) / std
                    image_from_mongo = celebrity_schema.Image.objects(name=f).first()
                    vecteur_image = image_from_mongo.vecteur_image
                    if vecteur_image == []:
                        embedding = get_embedding(model,image)
                        image_from_mongo.vecteur_image.append(np.array(embedding, dtype=float))
                        images.append(image)
                        labels.append(dire)
                        names.append(f)
                        embeddings.append(image_from_mongo.vecteur_image)
                        image_from_mongo.save()
                    else:
                        images.append(image)
                        labels.append(dire)
                        names.append(f)
                        embeddings.append(vecteur_image)

    except Exception as e:
         print(str(e))
    return np.array(images), np.array(labels), np.array(names),np.array(embeddings)



def get_clean_data(dataset_path, labels, embeds, names, threshold=9, method='distance'):
    print("[INFO] wait to clean data from mongo/FS")
    outliers = {}
    clean_embed = []
    clean_labels = []
    for k in set(labels):

        if method == 'distance':
            filter = []
            center = sum(embeds[k]) / len(embeds[k])
            for e in embeds[k]:
                filter.append(norm(e - center))
            filter = np.array(filter)
            outliers[k] = np.array(names[k])[np.where(filter >= threshold)]
            celebrity = celebrity_schema.Celebrity.objects(name=k).first()
            if celebrity is not None:
                for img in celebrity.images:
                    if img.name in outliers[k]:
                        image_path = dataset_path + '/' + k + '/' + img.name
                        if os.path.exists(image_path):
                            os.remove(image_path)
                            img.delete()
                            celebrity.images.remove(img)
                            print('[INFO] The image ' + img.name + ' was deleted.')
                        else:
                            print("The file does not exist")

                celebrity.save()
                clean_embed.extend(np.array(embeds[k])[np.where(filter < threshold)])
                n = len(np.array(embeds[k])[np.where(filter < threshold)])
        clean_labels.extend([k] * n)
        # print(filter, np.array(names[k]))

    return outliers, np.array(clean_embed), np.array(clean_labels)

def get_dict_embedding_label_name(embeddings,labels,names):
    embeds_dict = defaultdict(list)
    names_dict = defaultdict(list)
    for i, k in enumerate(labels):
        embeds_dict[k].append(embeddings[i])
        names_dict[k].append(names[i])
    return embeds_dict,names_dict

def main():
    connexion.get_connexion()
    model = InceptionResNetV2()
    model.load_weights(PATH_FACENET)
    dataset_path = PATH_PHOTOS
    images, labels, names, embeddings = get_data(dataset_path,model)
    embeds_dict, names_dict = get_dict_embedding_label_name(embeddings, labels, names)
    outliers, clean_embed, clean_labels = get_clean_data(dataset_path,labels, embeds_dict, names_dict)
    return clean_embed,clean_labels

def main_kafka():
    connexion.get_connexion()
    model = InceptionResNetV2()
    model.load_weights(PATH_FACENET)
    dataset_path = PATH_PHOTOS
    dic_clean_data = {}
    images, labels, names, embeddings = get_data(dataset_path,model)
    embeds_dict, names_dict = get_dict_embedding_label_name(embeddings, labels, names)
    outliers, clean_embed, clean_labels = get_clean_data(dataset_path,labels, embeds_dict, names_dict)
    dic_clean_data['clean_embed'] = clean_embed
    dic_clean_data['clean_labels'] = clean_labels
    return dic_clean_data



