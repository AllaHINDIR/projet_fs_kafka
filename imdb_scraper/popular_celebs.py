import asyncio
import time
import aiohttp
import async_timeout
import requests
from bs4 import BeautifulSoup

def getListUrl(numberOfCeleb):
    #chaque page contient 50 celeb
    list_url = []
    for i in range(1,numberOfCeleb,50) :
        url = "https://www.imdb.com/search/name/?match_all=true&start=" + str(i) + "&ref_=rlm"
        list_url.append(url)
    #numberPage = numberOfCeleb / 50
    print(list_url)
    return list_url

async def fetch(session, url):
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()

async def soup_d(html, display_result=False):
    soup = BeautifulSoup(html, 'html.parser')
    if display_result:
        print(soup.prettify())
    return soup

async def extract_celeblist(html):
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

http_proxy = "http://20.47.108.204:8888"
https_proxy = "http://170.155.5.235:8080"

proxies = {
              "http": http_proxy,
              "https": https_proxy
            }

def getCelebrities(numberOfCeleb):
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



#getCelebrities(500)
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