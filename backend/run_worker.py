from app.workers.workers import spawn_logs_worker, spawn_register_worker
from app.core.tasks.fr_minio_tasks import get_register_events, get_logs_events

if __name__ == "__main__":
    # get_register_events()
    spawn_register_worker()
    # spawn_logs_worker()

# from app.core.analytics.job_updates import task_updater

# if __name__ == "__main__":
#     task_updater()
