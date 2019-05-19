import pyrealsense2 as rs
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
import os
import skimage.io
import datetime
import cv2
import time
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
    for i in range(15):
        pipeline.wait_for_frames()

    # Getting the depth sensor's depth scale (see rs-align example for explanation)
    depth_sensor = profile.get_device().first_depth_sensor()
    depth_scale = depth_sensor.get_depth_scale()
    
    # IR and RGB shutter speeds.
    # Note 10,000=1 second in RGB but 
    # IR is in us (e.g. 1,000,000
    # =1 second)
#     colour_sensor= profile.get_device().query_sensors()[1]	
#     colour_sensor.set_option(rs.option.exposure, 500)
#     colour_sensor.set_option(rs.option.gain, 10)


    align_to = rs.stream.color
    align = rs.align(align_to)

    # depth median
    aligned_depth_list = []
    color_frame = None
    aligned_depth_median = None
    frames_list = []
    
    for i in range(10):
        # Get frameset of color and depth
        frames = pipeline.wait_for_frames()
        # frames.get_depth_frame() is a 640x360 depth image

        # Align the depth frame to color frame
        aligned_frames = align.process(frames)

        # Get aligned frames
        aligned_depth_frame = aligned_frames.get_depth_frame() # aligned_depth_frame is a 640x480 depth image
        intrinsics = rs.video_stream_profile(aligned_depth_frame.profile).get_intrinsics()
        color_frame = aligned_frames.get_color_frame()
        aligned_depth_list.append(np.asanyarray(aligned_depth_frame.get_data()))

    aligned_depth_median = np.median(np.array(aligned_depth_list), axis=0)
    # Validate that both frames are valid
    if not aligned_depth_frame or not color_frame:
        raise SystemExit
    

    depth_image = aligned_depth_median
    color_image = np.asanyarray(color_frame.get_data())
    depth_image2 = 2**(-16) * depth_image
#     print(color_image[15,15,:])
#     print(depth_image[15,15])

    pipeline.stop()
    
    if isSavePic:
        
        PNG_DIR = os.path.join(ROOT_DIR, "logs")
        file_name = "color_{:%Y%m%dT%H%M%S}.png".format(datetime.datetime.now())
        pngFilePath = os.path.join(PNG_DIR, file_name)

        cv_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(pngFilePath, cv_image)
        cv2.imwrite(pngFilePath.replace("color","depth"), depth_image)
        # Render images
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        cv2.imwrite(pngFilePath.replace("color","depthImg"), depth_colormap)
        
#         np.savetxt(pngFilePath.replace("color","depth").replace(".png",""), depth_image)
    
#     # test start
#     depth_image = mpimg.imread(os.path.join(IMAGE_DIR, "depth_151553413886.png"))
#     color_image = skimage.io.imread(os.path.join(IMAGE_DIR, "color_151553413886.png"))
#     print(color_image[15,15,:])
#     print(depth_image[15,15])
#     # test end
    return (color_image,depth_image2,depth_scale,intrinsics,file_name)
