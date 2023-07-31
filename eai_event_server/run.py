from imports import time, datetime, logger
from faust_scripts.faust_vars import FaustAppCreateVars, BusinessLogics
from faust_manager.manager import FaustManager
from faust_scripts.faust_config import FaustConfig

logger.info('\n'*5+f"Event server started at {datetime.now()}")

manager = FaustManager()

def run_worker_spawner(app_name, pipeline_id):
    manager.spawn_workers(
        app_name=app_name,
        pipeline_id=pipeline_id,
        number_of_workers=1
    )
    time.sleep(20)


def repeat_spawner(repeat=1):
    for i in range(repeat):
        app_vars = FaustAppCreateVars(
            faust_app_id="pipeline_1",
            broker="kafka://localhost:8097",
            pipeline_topic_id="test_kafka_topic",
            business_logics=BusinessLogics(
                fake_agent_1=True,
                fake_agent_2=True,
                fake_agent_3=True,
            )
        )
        FaustConfig.create_faust_config(faust_vars=app_vars)
        run_worker_spawner(
            app_name="faust_app",
            pipeline_id=app_vars.faust_app_id,
        )

        # app_vars = FaustAppVars(
        #     faust_app_id="pipeline_2",
        #     broker="kafka://localhost:8097"
        # )
        # FaustConfig().create_faust_config(faust_vars=app_vars)
        # run_worker_spawner(
        #     app_name="faust_app",
        #     pipeline_id=app_vars.faust_app_id
        # )
        time.sleep(300)
        manager.stop_all_workers()

if __name__ == "__main__":
    repeat_spawner(repeat=1)




