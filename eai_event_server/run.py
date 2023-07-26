# from test_codes import (
#     manager, 
#     # kafka_data_gen, 
#     # faust_1
# )
from imports import time
from faust_manager.manager import FaustManager
manager = FaustManager()

def repeat_spawner(repeat=1):
    for i in range(repeat):
        manager.spawn_workers(
            app_name="faust_app",
            pipeline_id="pipeline_id",
            number_of_workers=3
        )
        time.sleep(20)
        manager.stop_all_workers()
        time.sleep(10)


if __name__ == "__main__":
    
    repeat_spawner(repeat=100)