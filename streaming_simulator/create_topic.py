from kafka.admin import KafkaAdminClient, NewTopic
import logging

logging.basicConfig(level=logging.INFO)

def create_topic():
    admin_client = KafkaAdminClient(
        bootstrap_servers=['localhost:9092']
    )
    
    topic = NewTopic(
        name='video_frames',
        num_partitions=1,
        replication_factor=1
    )
    
    try:
        admin_client.create_topics([topic])
        logging.info("Topic 'video_frames' created successfully")
    except Exception as e:
        logging.info(f"Topic might already exist: {e}")
    
    admin_client.close()

if __name__ == "__main__":
    create_topic()