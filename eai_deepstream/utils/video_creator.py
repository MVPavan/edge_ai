import os
import cv2
from pathlib import Path
import numpy as np
from tqdm import tqdm
import logging
tc_log  = logging.getLogger()


allowed_image_suffixes = [".jpg"]

class VideoProps:
    images_folder:str
    output_video_name:str=None
    height=480
    width=640
    fps=30
    fourcc = 'mp4v'
    img_list_filename=None


def preproc(img, input_size, swap=(0,1,2)):
    """
    input_size = HxW
    """
    if len(img.shape) == 3:
        padded_img = np.zeros((input_size[0], input_size[1], 3), dtype=np.uint8)
    else:
        padded_img = np.ones(input_size, dtype=np.uint8) * 114
    r = min(input_size[0] / img.shape[0], input_size[1] / img.shape[1])
    resized_img = cv2.resize(
        img,
        (int(img.shape[1] * r), int(img.shape[0] * r)),
        interpolation=cv2.INTER_LINEAR,
    ).astype(np.uint8)
    padded_img[: int(img.shape[0] * r), : int(img.shape[1] * r)] = resized_img
    padded_img = padded_img.transpose(swap)
    padded_img = np.ascontiguousarray(padded_img, dtype=np.uint8)
    # padded_img = np.ascontiguousarray(padded_img, dtype=np.float32)
    return padded_img, r

def images_to_video(vprops:VideoProps):
    images_folder = Path(vprops.images_folder)
    img_files = [fp for fp in images_folder.iterdir() if fp.suffix in allowed_image_suffixes]

    fourcc = cv2.VideoWriter_fourcc(*vprops.fourcc)
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    if vprops.output_video_name is None:
        output_video_path = images_folder.parent/f"{images_folder.name}.mp4"
    else:
        output_video_path = images_folder.parent/vprops.output_video_name
    
    video = cv2.VideoWriter(output_video_path.as_posix(), fourcc, vprops.fps, (vprops.width,vprops.height))

    if VideoProps.img_list_filename is None:
        imglist_file_path = images_folder.parent/f"{output_video_path.stem}.txt"
    else:
        imglist_file_path = images_folder.parent/(vprops.img_list_filename)

    with open(imglist_file_path.as_posix(), 'w+') as fpp:
        for imgfp in tqdm(img_files,desc="Images: "):
            image = cv2.imread(imgfp.as_posix())
            # resized=cv2.resize(image,vprops.shape)
            resized,r = preproc(image,(vprops.height,vprops.width))
            video.write(resized)
            fpp.write(imgfp.as_posix()+" " + str(round(r,3))+'\n')

    video.release()

    out_h264 = output_video_path.with_suffix(".h264").as_posix()
    os.system(f"ffmpeg -i {output_video_path.as_posix()} -vcodec libx264 {out_h264}")
    tc_log.info("finished saving to video!")


def check_frame_count(filename):
    cap = cv2.VideoCapture(filename)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    tc_log.info( length )

def check_frame_count_by_reading(filename):
    # Opens the Video file
    cap= cv2.VideoCapture(filename)
    i=1
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False: break
        i+=1
    cap.release()
    cv2.destroyAllWindows()
    tc_log.info("Frame Count: ",i)


def read_video_frame_idx(video_file,frame_number=0):
    capture = cv2.VideoCapture(video_file)
    # Set the frame position to the desired frame number
    capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    print('Frame count:', frame_count)
    ret, frame = capture.read()
    if ret:
        # Display the frame
        cv2.imwrite(f'output/temp_{frame_number}.jpg', frame)
        print("fetched successfully!")

    capture.release()
    cv2.destroyAllWindows()

if __name__=="__main__":
    # vprops = VideoProps()
    # vprops.images_folder = "/data/datasets/infer/org/coco_yolo_c10_val"
    # images_to_video(vprops=vprops)
    # img = cv2.imread("/data/nvidia_local/deepstream/data/test_10/000000580197.jpg")
    # img2,r = preproc(img,(544,960))
    # tc_log.info("herer")
    read_video_frame_idx(
        video_file="/data/CODES/nvidia_manthana/tycoai/acvs-tycoai-ds-triton-benchmark/benchmark_scripts/output/sample_30.mp4",
        frame_number=725
    )


"""
# Convert MPEG4 video file to MP4 container file
ffmpeg -i output.mpeg4 output.mp4 -y -loglevel quiet
ffprobe -i $TARGET_VIDEO_PATH -hide_banner
"""