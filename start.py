# Il s'agit du programme principal qui permet de lancer toute
# la pile des producteurs et les consommateurs de kafka d'une manière automatique

import time
from multiprocessing import Process
from Kafka.consumers import consumer_prod_urls,consumer_storage,consumer_entrianement
from Kafka.producers import producer_google_image,producer_tmdb,producer_nettoyage
from storage import mongodb
from celebritiesnames import get_celebrities


if __name__ == '__main__':

    print("Vous voulez des images pour des nouvelles célébrités ou bien ")
    print("pour des célébrités qui existent déjà dans la BD? ")
    print("Choisissez : ")
    print("N/n : des nouvelles célébrités")
    print("O/o : des anciennes célébrités")
    print("B/b : des nouvelles et anciennes célébrités")

    type_recherche = input("Saisissez votre choix : ")
    if type_recherche == 'o' or type_recherche == 'O':
        list = get_celebrities.get_mongo_name_celebrities()
        if list == []:
            print("Pas de célébrités sur la base de données ! Du coup le programme lance ")
            print("automatiquement une recherche des nouvelles célébrités.")
            type_recherche = 'n'
    list_searshKeys = []
    indice = 0
    while True:

        consumer1 = Process(target=consumer_prod_urls.consumerVerification)
        consumer2 = Process(target=consumer_storage.consumerStorage)

        producer1 = Process(target=producer_google_image.start, args=(type_recherche,list_searshKeys,))
        producer2 = Process(target=producer_tmdb.main)

        try:
            consumer1.start()
            consumer2.start()

        except Exception as e:
            print(str(e))
        time.sleep(2)

        try:
            producer1.start()
            if indice == 0:
                producer2.start()

        except Exception as ex:
            print(str(ex))
        producer1.join()
        if indice == 0:
            producer2.join()

        # clean data
        try:
            producer3 = Process(target=producer_nettoyage.getCleanData)

        except Exception as ex:
            print(str(ex))

        try:
            list_celebrities = mongodb.current_nmbr_image()
            list_celebrities_new_image = []
            for celeb in list_celebrities:
                list_celebrities_new_image.append(mongodb.count_new_image(celeb['name']))

            producer3.start()
            producer3.join()

            list_celebrities_after_clean = mongodb.current_nmbr_image()
            list_searshKeys = []
            if len(list_celebrities) == len(list_celebrities_after_clean):
                indice = 0
                for i in range(0, len(list_celebrities)):
                    if list_celebrities[i]['nmbr_image'] - list_celebrities_after_clean[i]['nmbr_image'] > 3:
                        searsh_key = {}
                        searsh_key['name'] = list_celebrities[i]['name']
                        searsh_key['profession'] = list_celebrities[i]['profession']
                        list_searshKeys.append(searsh_key)
                        indice = 1
                if indice == 0:
                    print("[END] La pile a fini sa recherche :) ")
                    break
                else:
                    type_recherche = 'e'
                    print("[INFO] La pile continue la recherche pour les célébrités suivantes : ")
                    print(list_searshKeys)
                    continue
        except Exception as ex:
            print(str(ex))
    try:
        consumer3 = Process(target=consumer_entrianement.consumerCleanData)
        consumer3.start()
    except Exception as ex:
        print(str(ex))

    consumer1.join()
    consumer2.join()
    consumer3.join()

