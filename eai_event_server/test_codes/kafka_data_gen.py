from imports import (
    sys, time, date, tqdm, socket, logger,
    BaseModel, Faker, 
    AdminClient, NewTopic, Producer,
)
logger.setLevel(20)

class FakerProfile(BaseModel):
    job: str
    company: str
    ssn: str
    residence: str
    blood_group: str
    website: list[str]
    username: str
    name: str
    sex: str
    address: str
    mail: str
    birthdate: date

class KafkaParams(BaseModel):
    bootstrap_servers: str = "localhost:8097"
    topic_name: str = "test_kafka_topic"
    partition: int = 10
    no_of_records: int = int(1e4)

kp = KafkaParams()
conf = {
    'bootstrap.servers': kp.bootstrap_servers,
    'client.id': socket.gethostname()
}

admin_client = AdminClient(conf)

def delete_topic(topic_name, sleep=5):
    # Call delete_topics to asynchronously delete topics, a future is returned.

    # check if topic exists
    topic_metadata = admin_client.list_topics(timeout=5)
    if topic_name not in set(t.topic for t in iter(topic_metadata.topics.values())):
        print("Topic {} does not exist".format(topic_name))
        return

    fs = admin_client.delete_topics([topic_name])
    # Check deletion result
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print("Topic {} requestion for deletion".format(topic))
        except Exception as e:
            print("Failed to delete topic {}: {}".format(topic, e))
    
    if sleep:
        time.sleep(sleep)
    return
    

def create_topic(topic_name, num_partitions=10, replication_factor=1):
    new_topics = [NewTopic(topic_name, num_partitions, replication_factor)]
    # Call create_topics to asynchronously create topics. A dict
    # of <topic,future> is returned.
    fs = admin_client.create_topics(new_topics)
    # Wait for each operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print("Topic {} created".format(topic))
        except Exception as e:
            print("Failed to create topic {}: {}".format(topic, e))


def faker_datagen():

    producer = Producer(conf)
    faker = Faker()

    pbar = tqdm(total=kp.no_of_records)
    for _ in range(kp.no_of_records):
        profile = FakerProfile.model_validate(faker.profile())
        #print(profile)
        #print(profile['username'])
        message = profile.model_dump_json()
        key=str(profile.ssn)
        producer.produce(topic=kp.topic_name, value=message, key=key)
        producer.flush()
        pbar.update(1)


from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import concurrent.futures
def faker_datagen_concurrent(topic_name=None,total_generators=10, max_workers=10):
    if topic_name:
        delete_topic(topic_name, sleep=5)
        create_topic(topic_name)
    # Create a ThreadPoolExecutor
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit faker_datagen function to the executor
        futures = [executor.submit(faker_datagen) for _ in range(total_generators)]
        # Ensure all futures complete
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # get the result (or raise exception)
            except Exception as e:
                print(f"Exception occurred: {e}")


if __name__ == "__main__":
    faker_datagen_concurrent(topic_name="test_kafka_topic", total_generators=30, max_workers=30)
    # faker_datagen()
    sys.exit()