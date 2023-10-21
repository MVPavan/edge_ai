
from imports import dataclass,logger, OmegaConf, DictConfig, ListConfig
from .ds_pipeline_base import DsPipelineBase, PipelineBaseVars

import uuid


PIPELINE_COMMONS_PATH = "ds_configs/pipeline_configs/pipeline_design/pipeline_common_tails.yml"
PIPELINE_COMMON_PROPERTIES_PATH = "ds_configs/pipeline_configs/pipeline_props/pipeline_common_props.yaml"

PIPELINE_COMMONS_YML = OmegaConf.load(PIPELINE_COMMONS_PATH)
PIPELINE_COMMON_PROPERTIES = OmegaConf.load(PIPELINE_COMMON_PROPERTIES_PATH)

@dataclass
class ElementKeys:
    branch_out = "branch_out"
    branch_in = "branch_in"
    branches_to_link = "branches_to_link"

def is_list(sub_pipeline_yml):
    return isinstance(sub_pipeline_yml, ListConfig)

def is_dict(sub_pipeline_yml):
    return isinstance(sub_pipeline_yml, DictConfig)

def is_str(sub_pipeline_yml):
    return isinstance(sub_pipeline_yml, str)


pipeline_base_vars = PipelineBaseVars(
    pipeline_id="test_pipeline_id",
    pipeline_name="test_pipeline",
    pipeline_props={}
)

class PipelineCreator(DsPipelineBase):
    def __init__(self, pipeline_design:DictConfig, pipeline_props:DictConfig):
        # Check pipeline design
        assert is_dict(pipeline_design), "pipeline design must be a yml dict on parent level"
        assert 'pipeline' in pipeline_design, "Parent element of pipline design must have pipeline key"
        pipeline_tree = pipeline_design.pipeline
        assert is_list(pipeline_tree), "pipeline design must be a yml list at components level"
        
        # Check pipeline props 
        assert is_dict(pipeline_props), "pipeline props must be a yml dict on parent level"
        self.pipeline_props = OmegaConf.merge(PIPELINE_COMMON_PROPERTIES, pipeline_props)
        
        pipeline_base_vars = PipelineBaseVars(
            pipeline_id=self.pipeline_props.pipeline_details.id,
            pipeline_name=self.pipeline_props.pipeline_details.name,
            pipeline_props=self.pipeline_props
        )
        super().__init__(pipeline_base_vars=pipeline_base_vars)
        self.reset_vars()
        self.create_pipeline(pipeline_tree, parent=True)
        if 'probes' in pipeline_design:
            self.add_probes(probe_yml=pipeline_design.probes)
        self.create_rtsp_server(properties=self.pipeline_props.rtsp)
    
    def reset_vars(self):
        self.last_key = ""
        self.Queue_Counter = 0
        self.unique_keys = []
        self.branch_link_dict = {}

    def pipeline_append(self, element:tuple, element_list:list):
        factory_name, user_name = element
        if "queue" not in user_name:
            assert user_name not in self.unique_keys, f"Duplicate key: {user_name}"
        element_list.append(element)
        self.unique_keys.append(user_name)
        return element_list
    
    def add_queue(self, element, element_list):
        if ("queue" in list(OmegaConf.to_container(element).keys())[0] or
            "queue" in self.last_key):
            return element_list
        
        element_list = self.pipeline_append(("queue", f"queue_{self.Queue_Counter}"), element_list)
        self.Queue_Counter += 1
        return element_list
    
    def branch_out_tee(self, element_list:list):
        tee_element = ("tee", f"tee_{self.last_key}")
        element_list = self.pipeline_append(tee_element, element_list)
        return element_list
    
    def branch_in_linking(self, branches_to_link_element):
        assert is_dict(branches_to_link_element) and len(branches_to_link_element)==1,\
                "Branch in should have exact one 'branches_to_link' dict element"
        
        branches_suffix = '_'.join(list(OmegaConf.to_container(branches_to_link_element).values())[0])
        meta_mux_user_name = f"metamux_{branches_suffix}"
        self.pipeline_props[meta_mux_user_name] = self.pipeline_props.metamux_props
        metamux_link_sequence = self.build_pipeline_from_list([("nvdsmetamux",meta_mux_user_name)], self.pipeline_props)
        logger.warning(f"nvdsmetamux: file-loop not working for ///file:/ type sources")
        for _key, _value in branches_to_link_element.items():
            assert _key==ElementKeys.branches_to_link, "Branch in should have branches_to_link key"
            assert is_list(_value)
            for branch_name in _value:
                assert branch_name in self.branch_link_dict, \
                    f"Branch: {branch_name} does not exist for linking"
                print(f"linking {branch_name} to metamux element")
                branch_link_sequence = self.branch_link_dict[branch_name]
                assert branch_link_sequence, f"Branch: {branch_name} link sequence is empty"
                self.link_metamux(any_plugin=branch_link_sequence[-1], metamux_plugin=metamux_link_sequence[0])
        return metamux_link_sequence

    def create_branch(self, branch):
        if is_dict(branch):
            for branch_name, branch_elements in branch.items():
                if branch_name==ElementKeys.branch_out:
                    branch_link_sequence = self.create_pipeline([branch])
                # TODO: Concurrency
                branch_link_sequence = self.create_pipeline(branch_elements)
                return branch_name, branch_link_sequence
        elif is_str(branch):
            common_elements = self.add_common_elements(branch)
            branch_link_sequence = self.create_pipeline(common_elements)
            return branch, branch_link_sequence
        
    def create_branch_out(self, branch_out_elements, element_list, link_sequence):
        element_list = self.branch_out_tee(element_list)
        link_sequence_with_tee = self.build_pipeline_from_list(element_list, self.pipeline_props)
        if link_sequence:
            self.join_link_sequences(link_sequence, link_sequence_with_tee)
        link_sequence = link_sequence + link_sequence_with_tee
        
        for branch in branch_out_elements:
            branch_name, branch_link_sequence = self.create_branch(branch)
            self.join_link_sequences(link_sequence, branch_link_sequence)
            if branch_name != ElementKeys.branch_out:
                assert branch_name not in self.branch_link_dict, "Duplicate branch names"
                self.branch_link_dict[branch_name] = branch_link_sequence
        return link_sequence

    def add_common_elements(self, common_elements_key):
        if not common_elements_key in PIPELINE_COMMONS_YML:
            raise ValueError(f"{common_elements_key} does not exist in Common components")
        common_elements = PIPELINE_COMMONS_YML.get(common_elements_key)
        for _element in common_elements:
            for _k,_v in _element.items():
                if not _k in self.unique_keys: continue
                new_k, idx = _k, 1
                while new_k in self.unique_keys:
                    new_k = f"{new_k}_{idx}"
                    idx += 1
                _element[new_k] = _element[_k]
                del _element[_k]        
        return common_elements


    
    def build_common_elements(self, element, pre_element_list, link_sequence):
        _link_sequence_pre = []
        if pre_element_list:
            _link_sequence_pre = self.build_pipeline_from_list(pre_element_list, self.pipeline_props)
            if link_sequence:
                self.join_link_sequences(link_sequence, _link_sequence_pre)
        link_sequence = link_sequence + _link_sequence_pre
        
        branch_name, branch_link_sequence = self.create_branch(element)
        if link_sequence:
            self.join_link_sequences(link_sequence, branch_link_sequence)
        link_sequence = link_sequence + branch_link_sequence
        return link_sequence


    def create_pipeline(self, pipeline_tree, parent=False):
        element_list, link_sequence = [], []
        for element in pipeline_tree:

            # Builds Common elements
            if is_str(element):
                link_sequence = self.build_common_elements(
                    element=element,
                    pre_element_list=element_list,
                    link_sequence=link_sequence
                )
                self.last_key = element
                element_list = []
                continue
            
            # Build user defined elements
            assert is_dict(element), f"Pipeline element must be a dict: {element}"
            assert len(element)==1, "Should pass only one element"
            if not parent or element_list:
                element_list = self.add_queue(element, element_list)
            for key,value in element.items():
                if is_str(value):
                    element_list = self.pipeline_append((value,key), element_list)
                    self.last_key = key
                elif key==ElementKeys.branch_out:
                    link_sequence = self.create_branch_out(
                        branch_out_elements=value,
                        element_list=element_list,
                        link_sequence=link_sequence
                    )
                    self.last_key = ElementKeys.branch_out
                    element_list = []
                elif key==ElementKeys.branch_in:
                    assert self.last_key == ElementKeys.branch_out, "branch_in must follow branch_out"
                    assert not element_list, "Element list should be empty for branch_in"
                    assert is_list(value) and len(value)==1 and ElementKeys.branches_to_link in value[0],\
                          "Branch in value should be a list of length 1 with 'branches_to_link' element \
                            containing list of all branches to be merged"
                    link_sequence = self.branch_in_linking(value[0])
                    element_list = self.add_queue(element, element_list)
                    self.last_key = element_list[-1][-1]
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
        
        if not parent:
            return link_sequence_tail

    def add_probes(self, probe_yml:DictConfig):
        assert is_list(probe_yml), "probe_yml must be a yml list"
        for probe in probe_yml:
            assert is_dict(probe) and len(probe)==1, "each probe must be a single dict element"
            for key, value in probe.items():
                if key.lower()=="fps":
                    self.add_fps_probe(self.pipeline, value)
                else:
                    logger.warning(f"Unknown probe request: {key}")

        