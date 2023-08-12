from imports import OmegaConf
from pipeline_scripts.pipelines.pipeline_creator import PipelineCreator
from pipeline_scripts.run_pipeline import run_pipeline

pipeline_design_path = "ds_configs/pipeline_configs/pipeline_design/od_pipeline.yml"
pipeline_properties_path = "ds_configs/pipeline_configs/pipeline_props/od_props.yaml"
pipeline_design = OmegaConf.load(pipeline_design_path)
pipeline_props = OmegaConf.load(pipeline_properties_path)
   
pipeline = PipelineCreator(pipeline_design=pipeline_design, pipeline_props=pipeline_props)
run_pipeline(pipeline)
print("Recieved Pipeline")
