import concurrent.futures
import json
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from kafka import KafkaProducer
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from celebritiesnames import get_celebrities

from storage import mongodb

class GoogleImageScraper():
    def __init__(self ,search_key="Donald Trump"):

        # check if chromedriver is updated
        try:
            options = Options()
            options.add_argument("headless")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
        except Exception as e:
            print("[EXCEPTION] There is an exception !")
            print(str(e))
            exit()

        self.driver = driver
        self.search_key = search_key
        self.url = "https://www.google.com/search?q=%s&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947" % (search_key['name'])

    def find_image_urls(self):
        print("[INFO] Scraping for image link... Please wait.")
        image_urls = []
        count = 0
        number_of_unable_click = 0
        self.driver.get(self.url)
        time.sleep(1.5)
        numero_image = 1
        while True:
            if mongodb.count_new_image(self.search_key['name']) >= 5 :
                break
            try:
                # find and click image
                imgurl = self.driver.find_element(by=By.XPATH,value='//*[@id="islrg"]/div[1]/div[%s]/a[1]/div[1]/img' % (str(numero_image)))
                imgurl.click()
                number_of_unable_click = 0
            except Exception:
                # print("[-] Unable to click this photo.")
                number_of_unable_click = number_of_unable_click + 1
                if (number_of_unable_click > 10):
                    print("[INFO] No more photos.")
                    break

            try:
                # select image from the popup
                time.sleep(1)
                class_names = ["n3VNCb"]
                images = [self.driver.find_elements(by=By.CLASS_NAME,value=class_name) for class_name in class_names if
                          len(self.driver.find_elements(by=By.CLASS_NAME,value=class_name)) != 0][0]

                for image in images:
                    # only download images that starts with https
                    src_link = image.get_attribute("src")
                    if ("https" in src_link):
                        print("[INFO] %d. %s" % (count, src_link))
                        producerGoogleImageLinks(self.search_key['name'],self.search_key['profession'],src_link,numero_image,'raw')
                        image_urls.append(src_link)
                        count += 1
                        break
            except Exception:
                print("[INFO] Unable to get link")

            try:
                # scroll page to load next image
                if (count % 3 == 0):
                    self.driver.execute_script("window.scrollTo(0, " + str(numero_image * 60) + ");")
                element = self.driver.find_element(by=By.CLASS_NAME,value="mye4qd")
                element.click()
                print("[INFO] Loading more photos")
                time.sleep(1.5)
            except Exception:
                time.sleep(1)
            except(KeyboardInterrupt):
                print("[INFO] Turnning off Scraper")
                break
            numero_image += 1
        self.driver.quit()
        print("[INFO] Google search ended")
        return image_urls

def producerGoogleImageLinks(name,profession,url,numeroimage,key):
    """
    Cette fonction permet de définir le producer de google images.
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
    topic_name = 'urls'
    producer = None
    try:
        producer = KafkaProducer(bootstrap_servers=['localhost:9092'],value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    except Exception as ex:
        print('Exception while connecting Kafka')
        print(str(ex))
    try:
        key_bytes = bytes(key, encoding='utf-8')
        #value_bytes = bytes(url, encoding='utf-8')
        value = {'name': name,'profession':profession.replace('"',' '), 'numeroImage':numeroimage ,'url': url}

        producer.send(topic_name, value=value,key=key_bytes)
        producer.flush()
        print('Message published successfully from producerDoodleImageLinks.')
    except Exception as ex:
        print('Exception in publishing message')
        print(str(ex))

def get_images(search_key) :
    """
    cette fonction permet d'initaliser un scrapeur google images et de lancer la recherche des images.
    :param search_key: le nome de la célébrité pour laquelle la recherche des images s'effectue.
    :return:
    """
    # Define file path
    gd = GoogleImageScraper(search_key)
    image_urls = gd.find_image_urls()

    # Release resources
    del gd

def start(typeOfCelebrity,list):
    """
    programme de lancement avec les threads en precisant le type de recheche.
    Soit la recherche des images pour des nouvelles célébrité.
    soit la recherche des images pour les anciens célébrité.
    soit de faire les deux en meme temps.
    :param typeOfCelebrity: le type de recherche.
    :param list: liste vide.
    :return:
    """
    if typeOfCelebrity == 'n' or typeOfCelebrity == 'N':
        search_keys2 = get_celebrities.get_new_name_celebrities()
    elif typeOfCelebrity == 'o' or typeOfCelebrity == 'O':
        search_keys2 = get_celebrities.get_mongo_name_celebrities()
    elif typeOfCelebrity == 'b' or typeOfCelebrity == 'B':
        search_keys2 = get_celebrities.get_mongo_name_celebrities() + get_celebrities.get_new_name_celebrities()
    elif typeOfCelebrity == 'e' or typeOfCelebrity == 'E':
        search_keys2 = list
    else:
        print('[ERROR] Please insert enter a valid value (n/o/b/e).')
        exit()
    #search_keys2 = ['Lionel Messi', 'Cristiano Ronaldo', 'Diego Maradona', 'Zinedine Zidane', 'Usain Bolt', 'David Beckham']
    #start = time.time()
    for i in range(0, len(search_keys2), 30):
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            executor.map(get_images, search_keys2[i:i + 30])
    #end = time.time()
    print("[Google] Fin de recherche d'images")

