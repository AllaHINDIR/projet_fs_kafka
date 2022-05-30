import json
import os
from time import sleep
from saveimage import save_image
from kafka import KafkaConsumer

PATH_PHOTOS = os.path.dirname(os.path.abspath('consumer_storage.py'))
PATH_PHOTOS = PATH_PHOTOS.removesuffix('Kafka\consumers') + '\photos'


def connect_kafka_consumer(topic_name):
    """
    Cette fonstion permet la creation d'un consomateur lié à un topic et un broker.
    :param topic_name: represente le nom du topic auquel le consommateur sera lié.
    :return: un objet consommateur
    """
    consumer = None
    try:
        consumer = KafkaConsumer(topic_name,group_id='mygroup2', auto_offset_reset='earliest',enable_auto_commit=True,
                                 bootstrap_servers=['localhost:9092'])
    except Exception as ex:
        print('Exception while connecting Kafka')
        print(str(ex))
    finally:
        return consumer

def consumerStorage():
    print('Running ConsumerStorage..')
    topic_name = 'urlsVerifie'

    try:
        consumer = connect_kafka_consumer(topic_name)
        if not os.path.exists(PATH_PHOTOS):
            print("[INFO] Images path not found. Creating a new folder.")
            os.makedirs(PATH_PHOTOS)
        for msg in consumer:
            my_json = msg.value.decode('utf8')
            data = json.loads(my_json)
            print("[Storage Consumer] " , data)
            image_path = os.path.join(PATH_PHOTOS, data['name'])
            if not os.path.exists(image_path):
                print("[INFO] Image path not found. Creating a new folder.")
                os.makedirs(image_path)
            #save_image.save_image_kafka(data['url'],data['numeroImage'],data['name'],data['profession'])
            save_image.save_image(data['url'],data['numeroImage'],image_path,data['name'],data['profession'])

    except KeyboardInterrupt:
        pass
    finally:
        print("Leave group and commit final offsets")
        consumer.close()


