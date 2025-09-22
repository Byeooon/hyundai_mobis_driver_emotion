import pyrealsense2 as rs
import numpy as np
import cv2

# RealSense 파이프라인 설정
pipeline = rs.pipeline()
config = rs.config()

# 스트림 설정: 컬러(RGB) 영상
# D435 모델은 보통 640x480 해상도를 안정적으로 지원합니다.
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# 스트리밍 시작
pipeline.start(config)

print("카메라 스트리밍을 시작합니다. 종료하려면 'q' 키를 누르세요.")

try:
    while True:
        # 프레임 데이터가 올 때까지 대기
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        
        # 프레임이 없는 경우 다음 루프로 넘어감
        if not color_frame:
            continue

        # 컬러 이미지를 NumPy 배열로 변환
        color_image = np.asanyarray(color_frame.get_data())

        # 화면에 이미지 표시
        cv2.imshow('RealSense Color Stream', color_image)

        # 'q' 키를 누르면 루프 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # 스트리밍 중지
    pipeline.stop()
    cv2.destroyAllWindows()
    print("스트리밍이 중지되었습니다.")