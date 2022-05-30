import time
from multiprocessing import Process
from Kafka.consumers import consumer_prod_urls,consumer_storage,consumer_entrianement
from Kafka.producers import producer_google_image,producer_tmdb,producer_nettoyage
from storage import mongodb


if __name__ == '__main__':
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

