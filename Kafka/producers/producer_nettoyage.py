import json
from kafka import KafkaProducer
from netoyage import netoyage


def producerCleaning(clean_embed,clean_labels,key):
    topic_name = 'dataclean'
    producer = None
    try:
        producer = KafkaProducer(bootstrap_servers=['localhost:9092'],value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    except Exception as ex:
        print('Exception while connecting Kafka')
        print(str(ex))
    try:
        key_bytes = bytes(key, encoding='utf-8')
        #value_bytes = bytes(url, encoding='utf-8')
        value = {'clean_embed': clean_embed, 'clean_labels':clean_labels}

        producer.send(topic_name, value=value,key=key_bytes)
        producer.flush()
        print('Message published successfully from ProducerCleaning:')
        print(value)
    except Exception as ex:
        print('Exception in publishing message')
        print(str(ex))

def getCleanData():
    print('Running ProducerCleaning...')
    try:
        clean_data = netoyage.main_kafka()
        producerCleaning(clean_data['clean_embed'].tolist(), clean_data['clean_labels'].tolist(), 'raw')
    except Exception as ex:
        print('Exception : ')
        print(str(ex))

