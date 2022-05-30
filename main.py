#Import libraries
import concurrent.futures
import os
import time

from celebritiesnames import get_celebrities
from googleScraper.GoogleImageScrapper import GoogleImageScraper
from netoyage import netoyage
from entrainement import model


def get_images(search_key) :
    # Define file path
    image_path = os.path.normpath(os.path.join(os.getcwd(), 'photos'))
    # Parameters
    number_of_images = 20

    # Main program
    image_scrapper = GoogleImageScraper(image_path,search_key, number_of_images)
    image_urls = image_scrapper.find_image_urls()

    # Release resources
    del image_scrapper

if __name__ == "__main__":

    search_keys2 = get_celebrities.get_mongo_name_celebrities()
    #search_keys2 = ['Lionel Messi', 'Cristiano Ronaldo', 'Diego Maradona', 'Zinedine Zidane', 'Usain Bolt', 'David Beckham']
    start = time.time()
    for i in range(0, len(search_keys2), 30):
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            executor.map(get_images, search_keys2[i:i + 30])
        break
    end = time.time()
    print(end - start)

    #déclanchement de netoyage
    #clean_embed, clean_labels = netoyage.main()

    #lancement de l'entrainement après avoir des nouvelles images
    #model.getModel(clean_embed, clean_labels)

