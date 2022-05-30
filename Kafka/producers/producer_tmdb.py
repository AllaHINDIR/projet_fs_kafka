import json
from kafka import KafkaProducer
import asyncio
import time
import aiohttp
from tmdb_scraper import popular_celebs

def producerTmdbLinks(name,url,numeroimage,key):
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
    try:
        celebrities = popular_celebs.main()
        time.sleep(15)
    except Exception as e:
        print(e)
    return celebrities


def getLowerName(name):
    try:
        lower_name = name.lower()
        new_string = lower_name.replace(' ', '-')
        return new_string
    except Exception as e:
        print(e)
        return None


async def extract_photo_link(html, celebrity):
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
    #start = time.time()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    result = asyncio.run(async_getCelebritiesPhotos(getListCelebrities()))
    #print('GET URLS : %f' % (time.time() - start))
    print("[Tmdb] Fin de recherche d'images")





