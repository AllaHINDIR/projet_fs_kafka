from mongoengine import connect


#The connexion to database
def get_connexion():
    """
    Cette fonction assure le fait d'établir la connexion avec la BD.

    ingeniance5 : pour le dernier test de la version 1
    ingeniance3 : pour le test de la version 2 (seulement le TMDB)
    ingeniance4 : pour le test de la version 2 (les deux scrapeurs)

    """
    connect(db="ingeniance3",host="localhost",port=27017)

