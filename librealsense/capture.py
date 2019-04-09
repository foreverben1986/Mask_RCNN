import pyrealsense2 as rs
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
import os
import skimage.io
# Root directory of the project
ROOT_DIR = os.path.abspath("../")
# Directory of images to run detection on
IMAGE_DIR = os.path.join(ROOT_DIR, "apple_images")

def capture(isSavePic=False):
    pipeline = rs.pipeline()

    config = rs.config()
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.rgb8, 30);
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30);
    profile = pipeline.start(config)


    # Capture 30 frames to give autoexposure, etc. a chance to settle
    for i in range(30):
        pipeline.wait_for_frames()

    # Getting the depth sensor's depth scale (see rs-align example for explanation)
    depth_sensor = profile.get_device().first_depth_sensor()
    depth_scale = depth_sensor.get_depth_scale()


    align_to = rs.stream.color
    align = rs.align(align_to)

    # Get frameset of color and depth
    frames = pipeline.wait_for_frames()
    # frames.get_depth_frame() is a 640x360 depth image

    # Align the depth frame to color frame
    aligned_frames = align.process(frames)

    # Get aligned frames
    aligned_depth_frame = aligned_frames.get_depth_frame() # aligned_depth_frame is a 640x480 depth image
    intrinsics = rs.video_stream_profile(aligned_depth_frame.profile).get_intrinsics()
    color_frame = aligned_frames.get_color_frame()

    # Validate that both frames are valid
    if not aligned_depth_frame or not color_frame:
        raise SystemExit

    depth_image = np.asanyarray(aligned_depth_frame.get_data())
    color_image = np.asanyarray(color_frame.get_data())
    depth_image = 2**(-16) * depth_image
    print(color_image[15,15,:])
    print(depth_image[15,15])

    pipeline.stop()
    
    if isSavePic:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.imshow(color_image, origin="upper")
        plt.savefig("test.png")
        plt.show()
    
#     # test start
#     depth_image = mpimg.imread(os.path.join(IMAGE_DIR, "depth_151553413886.png"))
#     color_image = skimage.io.imread(os.path.join(IMAGE_DIR, "color_151553413886.png"))
#     print(color_image[15,15,:])
#     print(depth_image[15,15])
#     # test end
    return (color_image,depth_image,depth_scale,intrinsics)
