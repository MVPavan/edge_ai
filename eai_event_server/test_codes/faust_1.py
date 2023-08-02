from imports import (
    date, logger,
    asyncio, faust, Worker, codecs
)


test_app = faust.App(
    'my_app', 
    broker='kafka://localhost:8097',
)
test_app.conf.web_enabled = False
test_app.conf.web_port = 6066

class Data(faust.Record, serializer='json'):
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

source_topic = test_app.topic('test_kafka_topic', value_type=Data)
sink_topic = test_app.topic('faust_sink_topic', value_type=Data)

message_count = 0

@test_app.agent(source_topic)
async def process_messages(messages):
    global message_count
    async for message in messages:
        # Parse the JSON message
        # logger.info(f"Received message: {message.ssn}")
        message_count += 1
        await sink_topic.send(value=message)


@test_app.timer(interval=1.0)
async def periodic_sender():
    global message_count
    logger.info(f"Message count: {message_count}")
    message_count = 0



# if __name__ == '__main__':
#     app.main()







# def start_faust_app():
#     worker = app.Worker(loglevel=20,)
#     worker.execute_from_commandline()

# # if __name__ == '__main__':
# #     start_faust_app()


# from multiprocessing import Process
# if __name__ == "__main__":
#     # Number of workers
#     num_workers = 10

#     processes = []
#     for _ in range(num_workers):
#         p = Process(target=start_faust_app)
#         p.start()
#         processes.append(p)

#     for p in processes:
#         p.join()




# async def start_worker(worker: Worker) -> None:
#     await worker.start()

# def manage_loop():
#     loop = asyncio.get_event_loop()
#     worker = Worker(app, loop=loop, loglevel=20)
#     try:
#         loop.run_until_complete(start_worker(worker))
#     finally:
#         # worker.stop_and_shutdown_loop()
#         print("done with this loop")
#         loop.run_until_complete(worker.stop())
#         loop.close()


# if __name__ == '__main__':
#     manage_loop()

