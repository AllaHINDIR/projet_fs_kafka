import json
from kafka import KafkaProducer
import asyncio
import time
import aiohttp
from tmdb_scraper import popular_celebs

def producerTmdbLinks(name,url,numeroimage,key):
    """
    Cette fonction permet de définir le producer de TMDB.
    ce producer est lié au broker 9092.
    il écrit dans le topic topic_name.
    il envoie les données suivantes :
    :param name: le nom de la célébrité
    :param profession: la profession de la célébrité
    :param url: le lien de l'image de la célébrité
    :param numeroimage: le numero de l'image
    :param key: la clé qui caractérise chaque donnée envoyée, dans notre chaque donnée va etre envoyée dans une ligne.
    :return: producer.
    """
    topic_name = 'urlsFromTmdb'
    producer = None
    try:
        print('Running ProducerTmdb...')
        producer = KafkaProducer(bootstrap_servers=['localhost:9092'],value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    except Exception as ex:
        print('Exception while connecting Kafka')
        print(str(ex))
    try:
        key_bytes = bytes(key, encoding='utf-8')
        #value_bytes = bytes(url, encoding='utf-8')
        value = {'name': name,'profession':'Actor', 'numeroImage':numeroimage ,'url': url}

        producer.send(topic_name, value=value,key=key_bytes)
        producer.flush()
        print('Message published successfully from producerTMDB:')
        print(value)
    except Exception as ex:
        print('Exception in publishing message')
        print(str(ex))


def getListCelebrities():
    """
    Cette fonction permet de récupérer les noms des célébrités à partir de scrapeur de tmdb des noms.
    :return: la liste des noms des célébrités.
    """
    try:
        celebrities = popular_celebs.main()
        time.sleep(15)
    except Exception as e:
        print(e)
    return celebrities


def getLowerName(name):
    """
    Elle permet d'écrire les noms en miniscule, puis enlever les '-'.
    :param name: le nom de la célébrité.
    :return: le nom avec les nouvelles modifications.
    """
    try:
        lower_name = name.lower()
        new_string = lower_name.replace(' ', '-')
        return new_string
    except Exception as e:
        print(e)
        return None


async def extract_photo_link(html, celebrity):
    """
    Cette fonction permet d'extraire les liens des images des célébrités à partir du code html.
    :param html: le code html de la page web du profil de la célébrité.
    :param celebrity: les infos de la célébrité.
    :return: liste des liens des images.
    """
    soup = await popular_celebs.soup_d(html)
    photolist = soup.find('ul', {"class": "images posters compact"})
    data_page = []
    if photolist != None:
        photos = photolist.findAll('a', {"class": "image"})
        for photo in photos:
            if photo != None:
                src = "https://image.tmdb.org" + photo.get('href')
                data_page.append(src)
                producerTmdbLinks(celebrity['celeb_nom'],src,photos.index(photo),'raw')
    return data_page


async def getCelebrityPhoto(celebrity):
    """
    Elle permet de créer une session client pour effectuer les requetes de récupération des pages web des célébrités.
    Puis, elle récupere le resultat de la fct extract_photo_link.
    :param celebrity: les infos de la célébrités.
    :return: un sictionnaire qui conient les infos de la célébrité plus les liens de ses images.
    """
    try:
        data_photo = {}
        start = time.time()
        async with aiohttp.ClientSession() as session:
            url = "https://www.themoviedb.org" + celebrity['celeb_url'] + "-" + getLowerName(
                celebrity['celeb_nom']) + "/images/profiles?language=fr"
            html = await popular_celebs.fetch(session, url)
            data_photo['celeb_nom'] = celebrity['celeb_nom']
            data_photo['profession'] = "Actor"
            data_photo['urls'] = await extract_photo_link(html, celebrity)
        if data_photo['urls'] != []:
            print('[INFO] Les photos de la page %s sont sauvegardées.' % (celebrity['celeb_nom']))
        else:
            print("[ATTENTION] Pas de photo pour %s !!!! OU le serveur a repondu par 403 " % (celebrity['celeb_nom']))
        # print("Temps d'execution : %f " % (time.time()-start))
        return data_photo
    except Exception as e:
        print(e)


async def async_getCelebritiesPhotos(celebrities):
    """
    Cette fonction permet de lancer plusieurs taches en mode asynchrone.
    :param celebrities: la liste des célébrités.
    :return: liste qui contient tous les resultats de toutes les taches.
    """
    data = []
    for i in range(0, len(celebrities), 60):
        tasks = [asyncio.create_task(getCelebrityPhoto(celebrity)) for celebrity in celebrities[i:i + 60]]
        await asyncio.gather(*tasks)
        for e in range(len(tasks)):
            data.append(tasks[e].result())
        await asyncio.sleep(30)
    # print(tasks[0].result())
    # data =[tasks[i].result() for i in range(len(tasks))]
    return data


def main():
    """
    Programme principale qui lance l'execution du scrapeur en mode asynchrone.
    :return: Pas de valeur precise.
    """
    #start = time.time()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    result = asyncio.run(async_getCelebritiesPhotos(getListCelebrities()))
    #print('GET URLS : %f' % (time.time() - start))
    print("[Tmdb] Fin de recherche d'images")





