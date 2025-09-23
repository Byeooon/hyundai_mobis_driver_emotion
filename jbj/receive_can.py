import can
import cantools
import pandas as pd
import time
import os
import signal
import sys

def receive_can_to_csv(bus, dbc_file, save_path, signal_list=None):
    """
    CAN 데이터를 받아서 CSV 파일로 저장하는 함수 (Ctrl+C로 종료)

    Args:
        bus: python-can 버스 객체
        dbc_file: dbc 파일 경로
        save_path: 저장할 디렉토리
        signal_list: 관심 있는 신호 이름 리스트 (None이면 전체 저장)
    """
    # DBC 로드
    db = cantools.database.load_file(dbc_file)

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # CSV 파일 이름 (시작 시간 기준)
    start_time = time.time()
    file_time = time.strftime("%Y%m%d_%H%M%S", time.localtime(start_time))
    csv_file = os.path.join(save_path, f"can_log_{file_time}.csv")

    # 로그 저장용 DataFrame
    df = pd.DataFrame()

    print("[INFO] Start receiving CAN data... (Press Ctrl+C to stop)")
    try:
        while True:
            msg = bus.recv(timeout=1.0)
            if msg is None:
                continue

            try:
                decoded = db.decode_message(msg.arbitration_id, msg.data)

                # 관심 신호만 필터링
                if signal_list:
                    decoded = {k: v for k, v in decoded.items() if k in signal_list}

                # 유닉스 타임 (소수점 6자리까지)
                timestamp = f"{time.time():.6f}"

                row = {"timestamp": timestamp, "can_id": hex(msg.arbitration_id)}
                row.update(decoded)

                # DataFrame에 추가
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

            except Exception:
                # 정의되지 않은 메시지 무시
                pass

    except KeyboardInterrupt:
        print("\n[INFO] Stopping CAN logging...")

    finally:
        # CSV 저장
        if not df.empty:
            df.to_csv(csv_file, index=False)
            print(f"[INFO] Saved CAN data to {csv_file}")
        else:
            print("[INFO] No CAN data received.")
        bus.shutdown()
        print("[INFO] CAN bus closed cleanly.")


if __name__ == "__main__":
    bus = None
    try:
        bus = can.interface.Bus(channel="can0", interface="socketcan")
        dbc_file = "/media/imlab/Samsung_T54/dms_rev1/dbc/C_CAN.dbc"

        signal_list = [
            "CR_Ems_AccPedDep_Pc",  # 가속 페달
            "CR_Brk_StkDep_Pc",     # 브레이크 페달
            "SAS_Angle",            # 조향각
            "CR_Ems_VehSpd_Kmh",    # 차량 속도
            "LAT_ACCEL",            # 횡가속도
            "LONG_ACCEL",           # 종가속도
            "YAW_RATE"              # 요 레이트
        ]

        receive_can_to_csv(bus, dbc_file, save_path="./CAN_LOGS", signal_list=signal_list)

    finally:
        if bus is not None:
            bus.shutdown()

