
from pathlib import Path
import logging
from omegaconf import OmegaConf
from .tc_vars import TritonVars, ImageVars, TcResultVars
from .triton_client import run_grpc_inference, get_triton_model_config
from .tc_stats_utils import analyse_triton_stats

output_folder = (Path(__file__).parent)/"output"
output_folder.mkdir(exist_ok=True, parents=True)
logging.basicConfig(
    # filename="output/tc_benchmark.log",
    format='%(asctime)s:%(levelname)s:%(message)s',
    # filemode='a+',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler(output_folder/"tc_benchmark.log"),
        logging.StreamHandler()
    ]
)
tc_log = logging.getLogger()
IMAGE_EXT = [".jpg"]
            
def main(model_name=""):
    # select model
    model_choice = OmegaConf.load('./tc_config.yml')[model_name]

    result_vars = TcResultVars()
    triton_vars = TritonVars() 
    image_vars = ImageVars()
    image_vars.input_folder = Path("/data/datasets/infer/org/coco_yolo_c10_val")
    image_vars.output_folder = Path("/data/datasets/infer/results/temp")
    image_vars.output_folder.mkdir(parents=True, exist_ok=True)

    images_path = [
        fp.as_posix() for fp in image_vars.input_folder.iterdir() if fp.suffix in IMAGE_EXT
    ]

    for idx, img_path in enumerate(images_path):
        image_vars.image_paths_dict[str(idx)] = img_path
    triton_vars.MODEL_NAME = model_choice
    
    run_grpc_inference(image_vars=image_vars, triton_vars=triton_vars, result_vars=result_vars)
    analyse_triton_stats()

if __name__ == "__main__":
    main()