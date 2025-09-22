import os
import pyrealsense2 as rs
import numpy as np
import cv2
import time
import datetime


def receive_realsense(d_name, save_flag, path, n_serial, fps, width, height, stop_event):
    #
    print(f"[INFO] PID[{os.getpid()}] '{d_name}' process is started.")  

    save_path = os.path.join(path, 'video')

    if not os.path.isdir(save_path):
        os.makedirs(save_path)
    
    FPS = fps       #15
    WIDTH = width  # 1280
    HEIGHT = height  #720

    # n_serial = "102422072555"

    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()

    # Get device product line for setting a supporting resolution
    pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()
    device_product_line = str(device.get_info(rs.camera_info.product_line))
    config.enable_device(n_serial)

    found_rgb = False
    for s in device.sensors:
        if s.get_info(rs.camera_info.name) == 'RGB Camera':
            found_rgb = True
            break
    if not found_rgb:
        print("The demo requires Depth camera with Color sensor")
        exit(0)


    
    if device_product_line == 'D400':
        config.enable_stream(rs.stream.color, WIDTH, HEIGHT, rs.format.bgr8, FPS)
        config.enable_stream(rs.stream.infrared, 1, WIDTH, HEIGHT, rs.format.y8, FPS)  #  적외선 카메라

    # Start streaming
    profile = pipeline.start(config)

    # --- IR 프로젝터 끄기 ---
    device = profile.get_device()
    for sensor in device.query_sensors():
        if sensor.supports(rs.option.emitter_enabled):
            sensor.set_option(rs.option.emitter_enabled, 0)  # 0=OFF, 1=ON  적외선 카메라 점 패턴 없애기.
    print("[INFO] IR Emitter OFF (점 패턴 제거됨)")

    try:
        while True:

            # Wait for a coherent pair of frames: depth and color
            frames = pipeline.wait_for_frames()

            ts = time.time()
            cur_time = datetime.datetime.fromtimestamp(ts)

            formatted = cur_time.strftime("%Y%m%d_%H_%M_%S") + f".{int(cur_time.microsecond/1000):03d}"

            color_frame = frames.get_color_frame()
            ir_frame = frames.get_infrared_frame(1)   #  적외선 프레임도 가져옴

            if not color_frame or not ir_frame:
                continue

            # Convert images to numpy arrays
            color_image = np.asanyarray(color_frame.get_data())

            ir_image = np.asanyarray(ir_frame.get_data())
            ir_image = cv2.cvtColor(ir_image, cv2.COLOR_GRAY2BGR)
            
            color_path = os.path.join(save_path, f"{formatted}.png")
            # Save images
            suceess = cv2.imwrite(os.path.join(save_path, f"{formatted}.png"), color_image)
            if not suceess:
                print("[ERROR] Failed to save color image")
            else:
                print("[INFO] Saved:", color_path)


            cv2.imwrite(os.path.join(save_path, f"{formatted}_ir.png"), ir_image)

            # Show images
            resize_img = cv2.resize(color_image, (640, 480))

            cv2.namedWindow('color_img', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('color_img', resize_img)

            resize_img_ir = cv2.resize(ir_image, (640, 480))
            cv2.namedWindow('IR_img', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('IR_img', resize_img_ir)


            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            if stop_event and stop_event.is_set():
                break

    finally:

        # Stop streaming
        pipeline.stop()
        cv2.destroyAllWindows()
        print(f"[INFO] PID[{os.getpid()}] '{d_name}' process is terminated.")


if __name__ == '__main__':

    realsense_ctx = rs.context()  # The context encapsulates all of the devices and sensors, and provides some additional functionalities.
    connected_devices = []

    # get serial numbers of connected devices:
    for i in range(len(realsense_ctx.devices)):
        detected_camera = realsense_ctx.devices[i].get_info(
        rs.camera_info.serial_number)
        connected_devices.append(detected_camera)

    print(connected_devices)  #모든 realsense 카메라의 시리얼 넘버 리스트 반환
    print(os.getcwd())
    save_flag = True
    d_name = 'video'
    DATASET_PATH = os.getcwd()


    receive_realsense(d_name, save_flag, DATASET_PATH, '043322071182',30, 640, 480, None)
