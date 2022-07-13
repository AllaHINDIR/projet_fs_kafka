import json
from time import sleep

from kafka import KafkaConsumer
from entrainement import model

def connect_kafka_consumer(topic_one_name):
    """
    Cette fonction permet de connecter le consumer d'entrainement au broker 9092, et au topic donné en parametre.
    :param topic_one_name: le nom du topic qui va etre lié au consumer.
    :return: le consumer d'entrainement.
    """
    consumer = None
    try:
        consumer = KafkaConsumer(topic_one_name,group_id='mygroup3', auto_offset_reset='earliest',enable_auto_commit=True,  bootstrap_servers=['localhost:9092'])
    except Exception as ex:
        print('Exception while connecting Kafka')
        print(str(ex))
    finally:
        return consumer


def consumerCleanData():
    """
    Cette fonction permet au consumer d'entrainement de consommer les données stocker dans le topic topic_name.
    et produire le model de classification.
    :return: aucune valeur bien precise.
    """
    print('Running ConsumerCleanData..')
    topic_name = 'dataclean'
    try:
        consumer = connect_kafka_consumer(topic_name)

        for msg in consumer:
            my_json = msg.value.decode('utf8')
            data = json.loads(my_json)
            print("[Model Consumer] " , data)
            #model.getModel(data['clean_embed'],data['clean_labels'])

    except KeyboardInterrupt:
        pass
    finally:
        print("Leave group and commit final offsets")
        consumer.close()

