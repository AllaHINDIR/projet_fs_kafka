import asyncio
import time
import aiohttp
import async_timeout
import requests
from bs4 import BeautifulSoup

def getListUrl(numberOfCeleb):
    """
    Elle permet de récupérer les liens des pages webs qui contiennent les célébrités.
    :param numberOfCeleb: le nombre de célébrités qu'on veut récupérer
    :return: la liste des liens des pages webs.
    """
    #chaque page contient 50 celeb
    numberPage = int(numberOfCeleb / 20)
    list_url = []
    for i in range(1,numberPage+1) :
        url = "https://www.themoviedb.org/person?language=fr&page=" + str(i)
        list_url.append(url)
    return list_url

def extract_string(string):
    """
    Elle permet d'extraire une partie de text à partir d'une chaine de caractère.
    :param string: la chaine des caractères.
    :return: une partie de la chaine.
    """
    try:
        found = string.removesuffix("?language=fr")
        return found
    except AttributeError:
        pass

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
    celeblist = soup.find('div', {"class": "results flex results_profile_card"})
    data_page = []
    if celeblist != None:
        celeb_detail_list = celeblist.findAll('div', {"class": "fifty_square"})
        for i in range(len(celeb_detail_list)):
            celeb_info = {}
            img_info = celeb_detail_list[i].find("div", {'class': 'image_content'})
            celeb_url = img_info.find("a").get('href')
            celeb_nom = img_info.find("a").get('alt')
            celeb_profession = "Actor"
            celeb_info['celeb_url'] = extract_string(celeb_url)
            celeb_info['celeb_nom'] = celeb_nom
            celeb_info['celeb_profession'] = celeb_profession
            if celeb_info['celeb_url'] != "" and celeb_info['celeb_nom'] != "" and celeb_info['celeb_profession'] != "":
                data_page.append(celeb_info)
        #print(data_page)
    return data_page


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
        #print("Temps d'execution : %f " %(time.time()- start))

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



def main() :
    """
    Programme principal qui lance les taches et récupere leurs résultats en mode async.
    :return: le resyltat des taches.
    """
    start = time.time()
    # getCelebrities(500)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    result = asyncio.run(async_getCelebrities(getListUrl(20)))
    print('GET CELEBRITIES : %f' %(time.time()-start))
    return result

