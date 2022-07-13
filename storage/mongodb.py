from storage import celebrity_schema
from storage import connexion

connexion.get_connexion()


def save_celebrity(name,profession ,filename, url):
    """
    Consiste à stcoker la celebrité et son image dans mongodb.
    :param name: le nom de la célébrité.
    :param profession: le secteur d'activité de la célébrité.
    :param filename: le nom de fichier image.
    :param url: le lien de l'image.

    """
    celebrity = celebrity_schema.Celebrity(name = name,categorie=profession)
    image_document = celebrity_schema.Image(url=url,name=filename)
    image_document.vecteur_image = []
    image_document.save()
    celebrity.images.append(image_document)
    celebrity.save()
    print('[INFO MONGODB] Image and Celebrity are saved.')

def store_images(name,profession ,filename,url) :
    """
    Consiste à stcoker la celebrité et son image dans mongodb.
    :param name: le nom de la célébrité.
    :param profession: le secteur d'activité de la célébrité.
    :param filename: le nom de fichier image.
    :param url: le lien de l'image.

    """
    try :
        celebrity_count = celebrity_schema.Celebrity.objects(name=name).count()
        if celebrity_count == 0 :
            print('[INFO] The celecbrity dont exists !...Wait to add it to DB.')
            return save_celebrity(name,profession,filename,url)
        else:
            for celebrity in celebrity_schema.Celebrity.objects(name=name):
                image_document = celebrity_schema.Image(url=url,name=filename)
                image_document.vecteur_image = []
                image_document.save()
                celebrity.images.append(image_document)
                celebrity.save()
                print('[INFO MONGODB] Image saved.')
    except Exception as ex:
        print('[ERROR] There is an exception : ',ex)

def count_new_image(name):
    """
        cette fonction permet de compter le nombre de nouvelles images enregistrées
    :param name: c'est le nom de la célébrité
    :return: le nombre de nouvelles images
    """
    count = 0
    celebrity = celebrity_schema.Celebrity.objects(name=name).first()
    for image in celebrity.images:
        if image.vecteur_image == []:
            count +=1
    return count



def current_nmbr_image():
    """
    cette fonction permet de compter le nombre d'image acctuelle pour chaque célébrité.
    :return: un dictionnaire qui contient la célébrité et le nombre d'image qu'il a.
    """
    celebrity_imageNumber = []
    for celebrity in celebrity_schema.Celebrity.objects:
        dict_name_image = {}
        dict_name_image['name'] = celebrity.name
        dict_name_image['profession'] = celebrity.categorie
        dict_name_image['nmbr_image'] = len(celebrity.images)
        celebrity_imageNumber.append(dict_name_image)
    return celebrity_imageNumber

