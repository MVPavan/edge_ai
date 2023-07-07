from imports import (
    Dict, Optional, Union,
    BaseModel, validator
)

from ds_consts.pipeline_consts import (
    PipelineChoicesManager,
    PipelineBaseVars,
    PipelineRequestVars,
    PipelineResponseVars,
    PipelineCollectionVars,
    PipelineConstructVars,
    PipelineConstructStatus
)


class PipelineManager:
    BASE_PORT = 9500

    def __init__(self) -> None:
        self.existing_pipelines:PipelineCollectionVars = PipelineCollectionVars(pipelines={})
        self.pipeline_choice_manager = PipelineChoicesManager()
        self.pipeline_port_map:Dict[str, int] = {}

    def get_pipeline(self, pipeline_id:str) -> Optional[PipelineConstructVars]:
        if pipeline_id in self.existing_pipelines.pipelines:
            return self.existing_pipelines.pipelines[pipeline_id]
        return None
    
    def check_pipeline_exists(self, pipeline_id:str) -> PipelineResponseVars:
        if pipeline_id in self.existing_pipelines.pipelines:
            pipeline_response = self.get_pipeline_response_vars(
                self.existing_pipelines.pipelines[pipeline_id],
                status=PipelineConstructStatus.id_exists
            )
        else:
            pipeline_response = self.get_pipeline_response_vars(
            PipelineRequestVars(pipeline_id=pipeline_id, pipeline_choice="", pipeline_name="", pipeline_props={}),
                status=PipelineConstructStatus.does_not_exist
            )
        return pipeline_response

    def add_pipeline(self, pipeline_request_vars:PipelineRequestVars) -> PipelineResponseVars:    
        if pipeline_request_vars.pipeline_id in self.existing_pipelines.pipelines:
            pipeline_response = self.get_pipeline_response_vars(
                pipeline_request_vars,
                status=PipelineConstructStatus.id_exists
            )
            return pipeline_response
        
        ds_pipeline_class = self.pipeline_choice_manager.get_pipeline_choice_class(
            pipeline_choice=pipeline_request_vars.pipeline_choice
        )

        pipeline_base_vars=PipelineBaseVars(**pipeline_request_vars.dict())
        pipeline_base_vars = self.set_pipeline_port(pipeline_base_vars)
        # create pipeline object
        pipeline_object = ds_pipeline_class(pipeline_base_vars=pipeline_base_vars)

        pipeline_construct = PipelineConstructVars(
            **pipeline_request_vars.dict(),
            pipeline_object=pipeline_object,
        )
        # add pipeline object to pipeline collection
        self.existing_pipelines.pipelines[pipeline_request_vars.pipeline_id] = pipeline_construct
        pipeline_response = self.get_pipeline_response_vars(
            pipeline_request_vars,
            status=PipelineConstructStatus.success
        )
        return pipeline_response
    
    def delete_pipeline(self, pipeline_id:str) -> PipelineResponseVars:
        pipeline_response = self.check_pipeline_exists(pipeline_id)
        if pipeline_response.status == PipelineConstructStatus.does_not_exist:
            return pipeline_response
        
        pipeline_construct = self.existing_pipelines.pipelines[pipeline_id]

        if pipeline_construct.pipeline_object is not None:
            if pipeline_construct.pipeline_object.stop_pipeline():
                del pipeline_construct
                self.existing_pipelines.pipelines.pop(pipeline_id)
                pipeline_response.status = PipelineConstructStatus.success
            else:
                pipeline_response.status = PipelineConstructStatus.failure
        return pipeline_response
    
    def get_pipeline_port(self, pipeline_id:str) -> int:
        port = -1
        pipeline_response = self.check_pipeline_exists(pipeline_id)
        if pipeline_response.status == PipelineConstructStatus.id_exists:
            port = self.get_port_parameter(pipeline_response)
        return port
    
    def set_pipeline_port(self, pipeline_base_vars:PipelineBaseVars,) -> PipelineBaseVars:
        port = self.BASE_PORT + len(self.pipeline_port_map)
        while port in self.pipeline_port_map.values():
            port += 1
        pipeline_base_vars = self.set_port_parameter(pipeline_base_vars, port)
        self.pipeline_port_map[pipeline_base_vars.pipeline_id] = port
        return pipeline_base_vars

    @staticmethod
    def set_port_parameter(pipeline_base_vars:PipelineBaseVars, port:int) -> PipelineBaseVars:
        pipeline_base_vars.pipeline_props["multi_uri_src"]["port"] = port
        return pipeline_base_vars

    @staticmethod
    def get_port_parameter(pipeline_base_vars:PipelineBaseVars) -> int:
        return pipeline_base_vars.pipeline_props["multi_uri_src"]["port"]

    @staticmethod
    def get_pipeline_response_vars(
            pipeline_request_vars:PipelineRequestVars, 
            status:str=PipelineConstructStatus.failure
        ) -> PipelineResponseVars:
        return PipelineResponseVars(**pipeline_request_vars.dict(),status=status)


pipeline_manager = None
def get_pipeline_manager() -> PipelineManager:
    global pipeline_manager
    if pipeline_manager is None:
        pipeline_manager = PipelineManager()
    return pipeline_manager

















