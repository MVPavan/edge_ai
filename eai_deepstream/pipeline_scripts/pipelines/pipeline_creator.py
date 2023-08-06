
from imports import dataclass, OmegaConf, DictConfig, ListConfig
from .ds_pipeline_base import DsPipelineBase, PipelineBaseVars

import uuid


pipeline_design_path = "ds_configs/pipeline_configs/pipeline_design/od_pipeline.yml"
pipeline_commons_path = "ds_configs/pipeline_configs/pipeline_design/pipeline_common_tails.yml"
pipeline_properties_path = "ds_configs/pipeline_configs/pipeline_props/od_props.yaml"
pipeline_common_properties_path = "ds_configs/pipeline_configs/pipeline_props/pipeline_common_props.yaml"

pipeline_yml = OmegaConf.load(pipeline_design_path).pipeline
pipeline_commons_yml = OmegaConf.load(pipeline_commons_path)


@dataclass
class ElementKeys:
    branch_out = "branch_out"
    branch_in = "branch_in"

def is_list(sub_pipeline_yml):
    return isinstance(sub_pipeline_yml, ListConfig)

def is_dict(sub_pipeline_yml):
    return isinstance(sub_pipeline_yml, DictConfig)

def is_str(sub_pipeline_yml):
    return isinstance(sub_pipeline_yml, str)

assert is_list(pipeline_yml), "pipeline_yml must be a list on parent level"

pipeline_base_vars = PipelineBaseVars(
    pipeline_id="test_pipeline_id",
    pipeline_name="test_pipeline",
    pipeline_props={}
)

class PipelineCreator(DsPipelineBase):
    def __init__(self, pipeline_yml, pipeline_base_vars:PipelineBaseVars):
        # Initialize the Object Detection Single Head pipeline
        pipeline_common_properties = OmegaConf.load(pipeline_common_properties_path)
        pipeline_props = OmegaConf.load(pipeline_properties_path)
        self.pipeline_props = OmegaConf.merge(pipeline_common_properties, pipeline_props)
        pipeline_base_vars.pipeline_props = self.pipeline_props
        super().__init__(pipeline_base_vars=pipeline_base_vars)
        
        self.last_key, self.Queue_Counter = "", 0
        self.unique_keys = []
        self.create_pipeline(pipeline_yml, parent=True)

    def pipeline_append(self, element:tuple, element_list:list):
        factory_name, user_name = element
        assert user_name not in self.unique_keys, f"Duplicate key: {user_name}"
        element_list.append(element)
        self.unique_keys.append(user_name)
        return element_list

    def branch_out(self, element_list:list):
        tee_element = ("tee", f"tee_{self.last_key}")
        element_list = self.pipeline_append(tee_element, element_list)
        return element_list

    def create_branch(self, branch):
        if is_dict(branch):
            for branch_name, branch_elements in branch.items():
                # TODO: Concurrency
                branch_link_sequence = self.create_pipeline(branch_elements)
                return branch_name, branch_link_sequence
        elif is_str(branch):
            # TODO: Load common components from commons.yml
            branch = pipeline_commons_yml.get(branch)
            branch_link_sequence = self.create_pipeline(branch)
            return branch, branch_link_sequence


    def create_pipeline(self, pipeline_yml, parent=False):
        element_list, link_sequence = [], []
        for element in pipeline_yml:
            
            assert is_dict(element), "pipeline_yml must be a list of dicts"
            if not parent:
                self.pipeline_append(("queue", f"queue_{self.Queue_Counter}"), element_list)
                self.Queue_Counter += 1

            for key,value in element.items():
                if is_str(value):
                    element_list = self.pipeline_append((value,key), element_list)
                    self.last_key = key
                elif key==ElementKeys.branch_out:
                    element_list = self.branch_out(element_list)
                    link_sequence = self.build_pipeline_from_list(element_list, self.pipeline_props)

                    for branch in value:
                        branch_name, branch_link_sequence = self.create_branch(branch)
                        self.join_link_sequences(link_sequence, branch_link_sequence)

                    self.last_key = ElementKeys.branch_out
                    element_list = []
                elif key==ElementKeys.branch_in:
                    assert self.last_key == ElementKeys.branch_out, "branch_in must follow branch_out"
                    # TODO: Implement nvmetamux, add to element list
                else:
                    raise NotImplementedError

        link_sequence_tail=[]
        if element_list:
            link_sequence_tail = self.build_pipeline_from_list(element_list, self.pipeline_props)
        if link_sequence:
            if link_sequence_tail:
                self.join_link_sequences(link_sequence, link_sequence_tail)
            else:
                link_sequence_tail = link_sequence
        
        if parent:
            return self.pipeline
        else:
            return link_sequence_tail

                        
                    
PipelineCreator(pipeline_yml=pipeline_yml, pipeline_base_vars=pipeline_base_vars)

        