from imports import logger, Gst
from pipelines.pipeline_choices import ODSingleHead

if __name__=="__main__":
    osd_single_head = ODSingleHead()
    osd_single_head.build_pipeline()
    print("osd")