from imports import Path, CWD

FAUST_CONFIG_PATH = Path(__file__).resolve().parent/"faust_config.yml"
FAUST_LOGS_PATH = CWD/"logs/faust_logs"
FAUST_APP_DATA_PATH = FAUST_LOGS_PATH/"faust_app_data"
FAUST_CONFIGS_BACKUP = FAUST_APP_DATA_PATH/"faust_configs_backup"

FAUST_CONFIGS_BACKUP.mkdir(parents=True, exist_ok=True)

