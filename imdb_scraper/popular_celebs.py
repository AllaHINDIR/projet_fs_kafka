import asyncio
import time
import aiohttp
import async_timeout
import requests
from bs4 import BeautifulSoup

def getListUrl(numberOfCeleb):
    """
    Cette fonction permet de collecter les liens des pages web qui contiennent les differentes célébrités.
    :param numberOfCeleb: nombre max de célébrités à récupérer.
    :return: la listes des liens des page web qui contiennent les célébrités.
    """
    #chaque page contient 50 celeb
    list_url = []
    for i in range(1,numberOfCeleb,50) :
        url = "https://www.imdb.com/search/name/?match_all=true&start=" + str(i) + "&ref_=rlm"
        list_url.append(url)
    #numberPage = numberOfCeleb / 50
    print(list_url)
    return list_url

async def fetch(session, url):
    """
    Elle permet de recupérer la reponse d'une requete HTTP.
    :param session: la session de client sur laquelle la requete sera executée.
    :param url: l'url de la requete http.
    :return: le text de la reponse.
    """
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()

async def soup_d(html, display_result=False):
    """
    Cette fonction permet de transformer un objet html en un objet python en utilisant BeautifulSoup.
    :param html: le code html de la page web.
    :param display_result: paramertre pour ne pas afficher le resultat.
    :return: l'objet python.
    """
    soup = BeautifulSoup(html, 'html.parser')
    if display_result:
        print(soup.prettify())
    return soup

async def extract_celeblist(html):
    """
    Cette fonction consiste à parcourir l'objet python et extraire les infos des célébrités.
    :param html: le code html de la page web qui contient plusieurs célébrités.
    :return: la liste des infos des différentes célébrités détéctés.
    """
    soup = await soup_d(html)
    celeblist = soup.find('div', {"class": "lister-list"})
    data_page = []
    if celeblist != None:
        celeb_detail_list = celeblist.findAll('div', {"class": "lister-item mode-detail"})
        for i in range(len(celeb_detail_list)):
            celeb_info = {}
            img_info = celeb_detail_list[i].find("div", {'class': 'lister-item-image'})
            celeb_url = img_info.find("a").get('href')
            celeb_nom = img_info.find("img").get('alt')
            celeb_profession = celeb_detail_list[i].find("div", {'class': 'lister-item-content'}).find('p').getText()
            celeb_info['celeb_url'] = celeb_url
            celeb_info['celeb_nom'] = celeb_nom
            celeb_info['celeb_profession'] = celeb_profession.strip().strip('\n')
            if '|' in celeb_info['celeb_profession']:
                celeb_info['celeb_profession'] = celeb_info['celeb_profession'][
                                                 :celeb_info['celeb_profession'].index('|')]
            else:
                celeb_info['celeb_profession'] = ""
            if celeb_info['celeb_url'] != "" and celeb_info['celeb_nom'] != "" and celeb_info['celeb_profession'] != "":
                data_page.append(celeb_info)
        print(data_page)
        return data_page
    else:
        print('ATTENTION')
        print(celeblist)

async def getCelebrityInfo(url) :
    """
    Cette fonction permet de créer une sessions client pour les requetes. Ensuite faire appel aux différentes
    fonctions.
    :param url: le lien de la page web qui contient les infos des célébrités.
    :return: le résultat de la fonction extract_celeblist.
    """
    try :
        start = time.time()
        async with aiohttp.ClientSession() as session:
            html = await fetch(session, url)
            data_page = await extract_celeblist(html)

        print('[INFO] Les célébrités de la page %s sont sauvegardés.' %(url))
        print("Temps d'execution : %f " %(time.time()- start))

        return data_page
    except Exception as e :
        print(e)

async def async_getCelebrities(urls):
    """
    Ctte fonction permet de lancer plusieurs taches en mode async.
    :param urls: la liste des page web qui contiennent les infos des célébrités.
    :return: le rsultat des différentes taches.
    """
    tasks = [asyncio.create_task(getCelebrityInfo(url)) for url in urls]
    await asyncio.gather(*tasks)
    #print(tasks[0].result())
    #data =[tasks[i].result() for i in range(len(tasks))]
    data = []
    for i in range(len(tasks)) :
        if tasks[i].result():
            data = data + tasks[i].result()
    #print(len(data))
    #print(data)
    return data


def getCelebrities(numberOfCeleb):
    """
    Cette fonction fait le meme travail que les autres fonction sauf que'elle est en mode synchrone.
    :param numberOfCeleb: nombre de célébrité à récupérer.
    :return: liste des infos des célébrités.
    """
    try :
        data = []
        nmbr_celeb_scrape = 1
        while nmbr_celeb_scrape <= numberOfCeleb :
            url = "https://www.imdb.com/search/name/?match_all=true&start=" + str(nmbr_celeb_scrape) + "&ref_=rlm"
            r = requests.get(url=url)
            soup = BeautifulSoup(r.text, 'html.parser')
            celeblist = soup.find('div', {"class": "lister-list"})

            if celeblist != None:
                celeb_detail_list = celeblist.findAll('div',{"class": "lister-item mode-detail"})
                for i in range(len(celeb_detail_list)) :
                    celeb_info = {}
                    img_info = celeb_detail_list[i].find("div", {'class': 'lister-item-image'})
                    celeb_url = img_info.find("a").get('href')
                    celeb_nom = img_info.find("img").get('alt')
                    celeb_profession = celeb_detail_list[i].find("div", {'class': 'lister-item-content'}).find('p').getText()
                    celeb_info['celeb_url'] = celeb_url
                    celeb_info['celeb_nom'] = celeb_nom
                    celeb_info['celeb_profession'] = celeb_profession.strip().strip('\n')
                    if '|' in celeb_info['celeb_profession'] :
                        celeb_info['celeb_profession'] = celeb_info['celeb_profession'][:celeb_info['celeb_profession'].index('|')]
                    else :
                        celeb_info['celeb_profession'] = ""
                    if celeb_info['celeb_url'] != "" and celeb_info['celeb_nom'] != "" and celeb_info['celeb_profession'] != "" :
                        data.append(celeb_info)

            nmbr_celeb_scrape = nmbr_celeb_scrape + 50
            print('[INFO] %d célébrités ont été sauvegardés.'%(nmbr_celeb_scrape-1))
        print(len(data))
        print(data)
    except Exception as e :
        print(e)



#start = time.time()
#getCelebrities(500)
#asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#asyncio.run(async_getCelebrities(getListUrl(1000)))
#print('execution : %f' %(time.time()-start))



def main() :
    """
    Programme principal qui lance les taches et récupere leurs résultats en mode async.
    :return: le resyltat des taches.
    """
    start = time.time()
    # getCelebrities(500)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    result = asyncio.run(async_getCelebrities(getListUrl(10)))
    print('GET CELEBRITIES : %f' %(time.time()-start))
    print(result)
    print(len(result))
    return result

if __name__ == '__main__':
    main()



"""
session = requests.Session()

session.proxies = {
  'http': 'http://20.47.108.204:8888',
  'https': 'http://170.155.5.235:8080'
}

url = 'https://www.google.com/'

response = session.get(url)
print(response.status_code)

"""