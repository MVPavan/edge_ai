import json
from pathlib import Path
import json
import numpy as np
import pandas as pd
import logging
tc_log  = logging.getLogger()


output_folder = (Path(__file__).parent.parent)/"output"
output_folder.mkdir(exist_ok=True, parents=True)

stats_file = output_folder/"tc_stats.csv"
stats_columns = [
    "model_name", "model_version", "infer_count",
    "total_infer_latency", "avg_infer_latency", "infer_fps",
    "total_server_latency", "avg_server_latency", "server_fps"
]


def save_stats_json(model_stats, file_name):
    with open(output_folder/file_name, "w+") as fp:
        json.dump(model_stats,fp)


def save_stats_df(tdf:pd.DataFrame):
    if stats_file.exists():
        stats_df = pd.read_csv(stats_file.as_posix())
    else:
        stats_df = pd.DataFrame(columns=stats_columns)

    stats_df = pd.concat([stats_df, tdf],axis=0)
    stats_df.to_csv(stats_file.as_posix(), header=True, index=False)

def format_df(df:pd.DataFrame):
    df.drop("batch_stats",axis=1,inplace=True)
    df.columns = df.columns.str.replace(".","_",regex=False)
    df.columns = df.columns.str.replace("inference_stats_","",regex=False)
    df = df.apply(pd.to_numeric, errors='coerce').fillna(df)
    return df

def analyse_triton_stats(end_file=output_folder/"end.json", start_file=output_folder/"start.json"):
    with open(start_file,'r') as fp:
        start_df = pd.json_normalize(json.load(fp)["model_stats"][0])
    with open(end_file,'r') as fp:
        end_df = pd.json_normalize(json.load(fp)["model_stats"][0])
    
    if len(start_df.T)<16:
        start_df = start_df.reindex(
            columns=start_df.columns.union(end_df.columns), fill_value=0
        )
        start_df = start_df.reindex(columns=end_df.columns)

    start_df = format_df(start_df)
    end_df = format_df(end_df)

    assert (start_df.name == end_df.name).all() and (start_df.version == end_df.version).all(), "Start and end_df files are not for same model"

    tdf = pd.DataFrame(columns=stats_columns)
    tdf.model_name = end_df.name
    tdf.model_version = end_df.version

    tdf.infer_count = end_df.inference_count - start_df.inference_count

    tdf.total_infer_latency = (end_df.compute_infer_ns - start_df.compute_infer_ns)/(10**6)
    tdf.avg_infer_latency = tdf.total_infer_latency/tdf.infer_count
    tdf.infer_fps = 1000/tdf.avg_infer_latency

    start_duration = start_df.compute_input_ns + start_df.compute_infer_ns + start_df.compute_output_ns

    end_duration = end_df.compute_input_ns + end_df.compute_infer_ns + end_df.compute_output_ns
    
    tdf.total_server_latency = (end_duration - start_duration)/(10**6)
    tdf.avg_server_latency = tdf.total_server_latency/tdf.infer_count
    tdf.server_fps = 1000/tdf.avg_server_latency

    tdf = tdf.round(2)
    tc_log.info("\n\nTriton Stats: \n"+tdf.T.to_string(header=False))
    save_stats_df(tdf=tdf)
