import json
import time
from time import sleep
from cash import verification
from kafka import KafkaConsumer,KafkaProducer



def connect_kafka_consumer(topic_one_name,topic_two_name):
    """
    Cette fonction permet de connecter le consumer de vérification au broker 9092, et aux topics donnés en parametre.
    :param topic_one_name: le nom du topic qui va etre lié au consumer.
    :param topic_two_name: le nom du topic qui va etre lié au consumer.
    :return: le consumer de vérification.
    """
    consumer = None
    try:
        consumer = KafkaConsumer(topic_one_name,topic_two_name,group_id='mygroup1', auto_offset_reset='earliest',enable_auto_commit=True,
                                 bootstrap_servers=['localhost:9092'])
    except Exception as ex:
        print('Exception while connecting Kafka')
        print(str(ex))
    finally:
        return consumer

def producerverification(data,key):
    """
    Cette fonction permet de définir le producteur verification.
    ce producteur est lié au broker 9092.
    il stocke les donnée dans le topic topic_name.
    :param data: les données à envoyer par le producteur.
    :param key: la clé qui caractérise chaque donnée envoyée, dans notre chaque donnée va etre envoyée dans une ligne.
    :return: un producteur
    """
    topic_name = 'urlsVerifie'
    producer = None
    try:
        producer = KafkaProducer(bootstrap_servers=['localhost:9092'],value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    except Exception as ex:
        print('Exception while connecting Kafka')
        print(str(ex))
    try:
        key_bytes = bytes(key, encoding='utf-8')
        #value_bytes = bytes(url, encoding='utf-8')
        value = data

        producer.send(topic_name, value=value,key=key_bytes)
        producer.flush()
        print('Message published successfully from producerVerification.')
    except Exception as ex:
        print('Exception in publishing message')
        print(str(ex))

def consumerVerification():
    """
    Cette fonstion permet au consumer de vérification de consommer les données récupérées
    et vérifier leur validité.
    Le consumer consomme les données envoyées dans les topic topic_one_name et topic_two_name.
    Puis, chaque donnée vérifiée il l'envoie par le producer de vérification.
    :return: pas de valeur precise.
    """
    print('Running ConsumerVerification..')
    topic_one_name = 'urls'
    topic_two_name = 'urlsFromTmdb'

    try:
        consumer = connect_kafka_consumer(topic_one_name, topic_two_name)
        for msg in consumer:
            my_json = msg.value.decode('utf8')
            data = json.loads(my_json)
            if verification.NotExistInMongodb(url=data['url']):
                print("[Verification Consumer] ", data)
                """
                    Envoyer ces message au consumer de stockage
                """
                producerverification(data,'raw')

    except KeyboardInterrupt:
        pass
    finally:
        print("Leave group and commit final offsets")
        consumer.close()


