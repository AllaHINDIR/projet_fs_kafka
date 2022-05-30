import json
from time import sleep

from kafka import KafkaConsumer
from entrainement import model

def connect_kafka_consumer(topic_one_name):
    consumer = None
    try:
        consumer = KafkaConsumer(topic_one_name,group_id='mygroup3', auto_offset_reset='earliest',enable_auto_commit=True,  bootstrap_servers=['localhost:9092'])
    except Exception as ex:
        print('Exception while connecting Kafka')
        print(str(ex))
    finally:
        return consumer


def consumerCleanData():
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

