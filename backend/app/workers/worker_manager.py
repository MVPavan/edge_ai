from app.db.utils.redis_utils import RJQ_Register, RJQ_Logs
from app.core.tasks.fr_minio_tasks import get_register_events, get_logs_events


def fr_register_worker(ttl="23h"):
    register_worker = RJQ_Register.enqueue(f=get_register_events, ttl=ttl)
    return register_worker


def fr_logs_worker(ttl="23h"):
    logs_worker = RJQ_Logs.enqueue(f=get_logs_events, ttl=ttl)
    return logs_worker
