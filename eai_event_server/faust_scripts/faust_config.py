from imports import (
    OmegaConf, Path
)
from config import FAUST_CONFIG_PATH, FAUST_CONFIGS_BACKUP
from .faust_vars import FaustAppCreateVars


class FaustConfig:

    @staticmethod
    def create_faust_config(faust_vars:FaustAppCreateVars):
        faust_vars_dict = faust_vars.model_dump()
        faust_config = OmegaConf.create(faust_vars_dict)
        print(FAUST_CONFIG_PATH)
        with open(FAUST_CONFIG_PATH, 'w') as fp:
            fp.write(OmegaConf.to_yaml(faust_config))
        with open(FAUST_CONFIGS_BACKUP/f"{faust_vars.faust_app_id}.yml", 'w') as fp:
            fp.write(OmegaConf.to_yaml(faust_config))

    @staticmethod
    def load_faust_config(config_file:str=None) -> FaustAppCreateVars:
        if config_file is None:
            config_file = FAUST_CONFIG_PATH
        else:
            assert Path(config_file).exists(), f"Config file {config_file} does not exist"

        faust_config = OmegaConf.load(config_file)
        faust_app_vars = FaustAppCreateVars(**OmegaConf.to_container(faust_config))
        return faust_app_vars
        

