import pickle

from entrainement.message import InceptionResNetV2


model = InceptionResNetV2()
model.load_weights('../facenet_keras_weights.h5')

clas = pickle.load(open('model.sav','rb'))

images, labels, names = get_data('ingeniance')
print(names)
embd = get_embeddings(model,images)
print(clas.predict(embd))
