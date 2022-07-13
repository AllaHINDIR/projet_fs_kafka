from mongoengine import Document, ListField, StringField, URLField,ReferenceField


class Image(Document):
    """
    le schéma de document image dans la BD.
    """
    meta = {"collection" : "Images"}
    name = StringField(required=True, min_length=1)
    url = URLField(required=True)
    vecteur_image = ListField(required=False)

class Celebrity(Document):
    """
    le schéma de document célébrité dans la BD.
    """
    meta = {"collection" : "celebrities"}
    name = StringField(required=True,min_length=1)
    categorie = StringField(required=False,min_length=1)
    images = ListField(ReferenceField(Image))



