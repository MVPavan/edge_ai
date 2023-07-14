from imports import Path

make_dir = lambda folder_path: folder_path.mkdir(parents=True, exist_ok=True)
configs_folder = Path(__file__).parent

infer_configs_folder = configs_folder/'infer_configs'
make_dir(infer_configs_folder)

pipline_props_folder = configs_folder/'pipeline_configs/pipeline_props'
make_dir(pipline_props_folder)

plugin_props_folder = configs_folder/'pipeline_configs/plugin_props'
make_dir(pipline_props_folder)

COCO_LABELS_FILE = configs_folder/'coco_labels.txt'