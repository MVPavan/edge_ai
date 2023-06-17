import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from bus_call import bus_call
from gi.repository import GObject, Gst, GLib, GstRtspServer
import argparse


def generate_element(element_name, pipeline, element_list=None, element_description=None):
    if not element_description:
        element_description = f"{element_name}_name"
    element = Gst.ElementFactory.make(element_name, element_description)
    if not element:
        raise f"Cannot generate {element_name}"
    pipeline.add(element)
    if element_list is not None:
        element_list.append(element)
    return element

def start_pipeline(pipeline):
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)
    print("Starting pipeline \n")
    # start play back and listed to events
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except:
        pass

    # cleanup
    print("Exiting app\n")
    pipeline.set_state(Gst.State.NULL)

def createArgparse():
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-p", "--port", help="The rtsp port", default=8554, type=int)
    argParser.add_argument("-u", "--udp_port", help="The udp port", default=5150, type=int)
    argParser.add_argument("-l", "--loop", help="Loop", default=True, type=bool)

    return argParser

if __name__ == "__main__":
    argParser = createArgparse()
    args = argParser.parse_args()
    RTSP_PORT = args.port
    UDP_PORT = args.udp_port
    TAG = "/dsrtsp"
    LOOP = args.loop
    FILE_SOURCE =  "/opt/nvidia/deepstream/deepstream/samples/streams/sample_720p.h264"
    qtdemux = None
    is_h264 = FILE_SOURCE.endswith(".h264") # 
    element_list = []
    print("Creating Pipeline")
    Gst.init(None)
    pipeline = Gst.Pipeline()
    if LOOP:
        multifilesrc = generate_element("multifilesrc", pipeline, element_list, element_description="source_0")
        multifilesrc.set_property("loop", LOOP)
        multifilesrc.set_property('location', FILE_SOURCE)
    else:
        file_source = generate_element("filesrc", pipeline, element_list, element_description="source_0")
        file_source.set_property('location', FILE_SOURCE)
    if not is_h264:
        qtdemux = generate_element("qtdemux", pipeline, element_list)
    h264parse = generate_element("h264parse", pipeline, element_list)
    nvv4l2decoder = generate_element("nvv4l2decoder", pipeline, element_list)
    nvv4l2h264enc = generate_element("nvv4l2h264enc", pipeline, element_list)
    rtph264pay = generate_element("rtph264pay", pipeline, element_list)
    udpsink = generate_element("udpsink", pipeline, element_list)

    nvv4l2h264enc.set_property("bitrate", 4000000)

    udpsink.set_property("port", UDP_PORT)
    udpsink.set_property("async", "0")
    udpsink.set_property("sync", "1")
    udpsink.set_property("host", '0.0.0.0')

    prev = None
    for el in element_list:
        if prev:
            prev.link(el)
        prev= el

    server = GstRtspServer.RTSPServer.new()
    server.props.service = "%d" % RTSP_PORT
    server.attach(None)

    factory = GstRtspServer.RTSPMediaFactory.new()
    factory.set_launch(f"( udpsrc name=pay0 \
                    port=%d buffer-size=524288 \
                    caps=\"application/x-rtp, media=video, \
                    clock-rate=90000, encoding-name=(string)%s, \
                    payload=96 \" )" % (UDP_PORT, "H264"))
    factory.set_shared(True)
    server.get_mount_points().add_factory(TAG, factory)

    print(f"\n *** DeepStream: Launched RTSP Streaming at rtsp://localhost:{RTSP_PORT}/{TAG} ***\n\n")

    start_pipeline(pipeline)


    
