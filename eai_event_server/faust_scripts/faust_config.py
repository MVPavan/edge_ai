from imports import (
    OmegaConf, Path
)
from config import FAUST_CONFIG_PATH, FAUST_CONFIGS_BACKUP
from .faust_vars import FaustAppVars


class FaustConfig:
    def create_faust_config(self, faust_vars:FaustAppVars):
        faust_vars_dict = faust_vars.model_dump()
        faust_config = OmegaConf.create(faust_vars_dict)
        with open(FAUST_CONFIG_PATH, 'w') as fp:
            fp.write(OmegaConf.to_yaml(faust_config))
        with open(FAUST_CONFIGS_BACKUP/f"{faust_vars.faust_app_id}.yml", 'w') as fp:
            fp.write(OmegaConf.to_yaml(faust_config))
        

