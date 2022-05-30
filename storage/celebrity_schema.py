from mongoengine import Document, ListField, StringField, URLField,ReferenceField


class Image(Document):
    meta = {"collection" : "Images"}
    name = StringField(required=True, min_length=1)
    url = URLField(required=True)
    vecteur_image = ListField(required=False)

class Celebrity(Document):
    meta = {"collection" : "celebrities"}
    name = StringField(required=True,min_length=1)
    categorie = StringField(required=False,min_length=1)
    images = ListField(ReferenceField(Image))



