import sys
import time
import datetime
import csv
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, 
    QGridLayout, QTextEdit, QLabel, QFileDialog, QMessageBox, QHBoxLayout
)
from PyQt6.QtGui import QColor

# 감정 로거 애플리케이션 클래스
class EmotionLogger(QWidget):
    def __init__(self):
        super().__init__()
        self.log_file = 'emotion_log.csv'
        self.initUI()

    def initUI(self):
        # 윈도우 기본 설정
        self.setWindowTitle('감정 기록기')
        self.setGeometry(300, 300, 450, 450)

        # 글자색에 사용할 색상 정의 (딕셔너리 형태)
        self.emotion_colors = {
            '행복 😄': '#FF851B',  # 주황 (Orange)
            '중립 😐': '#FFDC00',  # 노랑 (Yellow)
            '지루함 😑': '#2ECC40',  # 초록 (Green)
            '우울 😔': '#0074D9',  # 파랑 (Blue)
            '두려움 😨': '#B10DC9',  # 보라 (Purple)
            '화 😡':   '#FF4136'   # 빨강 (Red)
        }

        # 전체 레이아웃 (수직)
        main_layout = QVBoxLayout()

        # --- 감정 버튼 부분 ---
        button_layout = QGridLayout()
        positions = [(i, j) for i in range(2) for j in range(3)]
        
        # 딕셔너리를 사용하여 버튼 생성
        for position, (emotion, color) in zip(positions, self.emotion_colors.items()):
            button = QPushButton(emotion)
            
            # 스타일시트 수정: 배경색(background-color)은 빼고 글자색(color)만 지정
            button.setStyleSheet(f"""
                QPushButton {{
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                    color: {color};
                }}
            """)
            button.clicked.connect(lambda checked, emo=emotion: self.log_emotion(emo))
            button_layout.addWidget(button, *position)

        # --- 로그 표시 부분 ---
        log_label = QLabel('기록된 감정 로그:')
        log_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("font-size: 14px;")
        
        # --- 기능 버튼들 (초기화, 내보내기) ---
        action_button_layout = QHBoxLayout()

        self.clear_button = QPushButton('로그 초기화 🗑️')
        self.clear_button.setStyleSheet("font-size: 14px; padding: 8px;")
        self.clear_button.clicked.connect(self.clear_logs)
        
        self.export_button = QPushButton('CSV로 내보내기 💾')
        self.export_button.setStyleSheet("font-size: 14px; padding: 8px;")
        self.export_button.clicked.connect(self.export_to_csv)

        action_button_layout.addWidget(self.clear_button)
        action_button_layout.addWidget(self.export_button)

        # 위젯들을 메인 레이아웃에 추가
        main_layout.addLayout(button_layout)
        main_layout.addWidget(log_label)
        main_layout.addWidget(self.log_display)
        main_layout.addLayout(action_button_layout)

        self.setLayout(main_layout)
        
        self.load_logs()

    def log_emotion(self, emotion):
        timestamp = int(time.time())
        try:
            with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, emotion])
        except IOError as e:
            self.log_display.append(f"파일 쓰기 오류: {e}")
            return
        readable_time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{readable_time}] 감정 기록: {emotion}"
        self.log_display.append(log_entry)

    def load_logs(self):
        if not os.path.exists(self.log_file):
            self.log_display.setText("로그 파일이 없습니다. 첫 감정을 기록해보세요!")
            return
        self.log_display.clear()
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) == 2:
                        timestamp, emotion = row
                        readable_time = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
                        log_entry = f"[{readable_time}] 감정 기록: {emotion}"
                        self.log_display.append(log_entry)
        except (IOError, ValueError) as e:
            self.log_display.append(f"로그 파일 읽기 오류: {e}")

    def export_to_csv(self):
        if not os.path.exists(self.log_file):
            self.log_display.append("내보낼 로그 파일이 없습니다.")
            return
        options = QFileDialog.Option.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(self, 
                                                   "CSV 파일로 저장", 
                                                   f"emotion_log_{int(time.time())}.csv",
                                                   "CSV Files (*.csv);;All Files (*)", 
                                                   options=options)
        if file_path:
            try:
                with open(self.log_file, 'r', encoding='utf-8') as src, \
                     open(file_path, 'w', newline='', encoding='utf-8') as dst:
                    writer = csv.writer(dst)
                    writer.writerow(['Timestamp', 'Emotion', 'ReadableTime'])
                    reader = csv.reader(src)
                    for row in reader:
                        if len(row) == 2:
                            timestamp, emotion = row
                            readable_time = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
                            writer.writerow([timestamp, emotion, readable_time])
                self.log_display.append(f"\n>> 로그가 '{file_path}'에 저장되었습니다.")
            except (IOError, ValueError) as e:
                self.log_display.append(f"\n>> 파일 내보내기 오류: {e}")
                
    def clear_logs(self):
        if not os.path.exists(self.log_file):
            self.log_display.append("\n>> 초기화할 로그가 없습니다.")
            return
        reply = QMessageBox.question(self, '로그 초기화 확인', 
                                     '정말로 모든 감정 기록을 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.log_display.clear()
                os.remove(self.log_file)
                self.log_display.setText("모든 로그가 초기화되었습니다.")
            except OSError as e:
                self.log_display.setText(f"파일 삭제 중 오류 발생: {e}")

# 프로그램 실행 부분
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EmotionLogger()
    window.show()
    sys.exit(app.exec())