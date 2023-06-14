import json
from pathlib import Path
import json
import pandas as pd
import numpy as np
import logging
tc_log  = logging.getLogger()
from utils.ds_vars import DsResultVars
from utils.tc_vars import ModelChoice


output_folder = (Path(__name__).parent)/"output"
output_folder.mkdir(exist_ok=True, parents=True)

stats_file = output_folder/"ds_stats.csv"
stats_columns = [
    "model_name", "b1", "b4", "b8", "b16", "b32"
]


def analyse_ds_stats(result_vars:DsResultVars, model_choice:ModelChoice):
    tdf_dict = {key:np.nan for key in stats_columns}
    for model_name, value in model_choice.__dict__.items():
        if value:
            tdf_dict["model_name"] = model_name
    batch_key = f"b{result_vars.batch_size}"
    tdf_dict[batch_key] = result_vars.fps

    tdf = pd.DataFrame(tdf_dict,index=[0])
    save_stats_df(tdf=tdf, mean_stats=result_vars.mean_stats)


def save_stats_df(tdf:pd.DataFrame, mean_stats=False):
    if stats_file.exists():
        stats_df = pd.read_csv(stats_file.as_posix())
    else:
        stats_df = pd.DataFrame(columns=stats_columns)

    stats_df = pd.concat([stats_df, tdf],axis=0)
    if mean_stats:
        stats_df = stats_df.groupby('model_name').mean().reset_index()
    stats_df = stats_df.round(3)
    stats_df.to_csv(stats_file.as_posix(), header=True, index=False)

def format_df(df:pd.DataFrame):
    df.drop("batch_stats",axis=1,inplace=True)
    df.columns = df.columns.str.replace(".","_",regex=False)
    df.columns = df.columns.str.replace("inference_stats_","",regex=False)
    df = df.apply(pd.to_numeric, errors='coerce').fillna(df)
    return df

if __name__=="__main__":
    analyse_ds_stats()