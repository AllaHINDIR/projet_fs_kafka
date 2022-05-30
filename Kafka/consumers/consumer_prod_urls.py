import json
import time
from time import sleep
from cash import verification
from kafka import KafkaConsumer,KafkaProducer



def connect_kafka_consumer(topic_one_name,topic_two_name):
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


