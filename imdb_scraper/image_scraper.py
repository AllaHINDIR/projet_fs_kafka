import asyncio
import time

import aiohttp

import popular_celebs

def getListCelebrities():
    try:
        celebrities = popular_celebs.main()
        time.sleep(15)
    except Exception as e:
        print(e)
    return celebrities

async def get_photo_link_original(link):
    photolink = None
    try :
        async with aiohttp.ClientSession() as session:
            html = await popular_celebs.fetch(session,link)
            soup = await popular_celebs.soup_d(html)
            photolink = soup.find('meta',{"property":"og:image"}).get('content')
    except Exception as e:
        print(e)
    return photolink

async def extract_photos_links(html):
    soup = await popular_celebs.soup_d(html)
    photosBoxslist = soup.find('div', {"class": "media_index_thumb_list"})
    data_page = []
    if photosBoxslist != None:
        photosBoxs = photosBoxslist.findAll('a')
        for photoBox in photosBoxs :
            if photoBox !=None :
                src = photoBox.get('href')
                photolink = await get_photo_link_original("https://www.imdb.com" + src)
                data_page.append(photolink)
                await asyncio.sleep(2)
        return data_page


async def getCelebrityPhoto(celebrity) :
    try :
        data_photo = {}
        start = time.time()
        async with aiohttp.ClientSession() as session:
            html = await popular_celebs.fetch(session, "https://www.imdb.com" + celebrity['celeb_url'] + "/mediaindex?ref_=nm_phs_md_sm")
            data_photo['urls'] = await extract_photos_links(html)
            data_photo['celeb_nom'] = celebrity['celeb_nom']
        print('[INFO] Les photos de la page %s sont sauvegardées.' %(celebrity['celeb_nom']))
        print("Temps d'execution : %f " %(time.time()- start))
        return data_photo
    except Exception as e :
        print(e)


async def async_getCelebritiesPhotos(celebrities):
    data = []
    for i in range(0,len(celebrities),100):
        tasks = [asyncio.create_task(getCelebrityPhoto(celebrity)) for celebrity in celebrities[i:i+100]]
        await asyncio.gather(*tasks)
        for e in range(len(tasks)):
            data.append(tasks[e].result())
        await asyncio.sleep(30)
    #print(tasks[0].result())
    #data =[tasks[i].result() for i in range(len(tasks))]
    return data



def main() :
    start = time.time()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    result = asyncio.run(async_getCelebritiesPhotos(getListCelebrities()))
    print('GET URLS : %f' %(time.time()-start))
    print(result)
    print(len(result))
    count =0
    for e in result:
        if e['urls'] == []:
            count += 1
    print(count)
    return result

if __name__ == '__main__':
    main()



