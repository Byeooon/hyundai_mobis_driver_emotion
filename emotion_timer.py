import sys
import time
import datetime
import csv
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QGridLayout, QTextEdit, QLabel, QFileDialog, QMessageBox, QHBoxLayout
)
from PyQt6.QtCore import QTimer, Qt

class EmotionLogger(QWidget):
    def __init__(self):
        super().__init__()
        self.log_file = 'emotion_log.csv'
        self.initUI()

    def initUI(self):
        self.setWindowTitle('감정 기록기')
        self.setGeometry(300, 300, 450, 450)
        self.remaining_time = 10
        self.emotion_colors = {
            '행복 😄': '#FF851B', '중립 😐': '#FFDC00', '지루함 😑': '#2ECC40',
            '우울 😢': '#0074D9', '두려움 😨': '#B10DC9', '화 😠': '#FF4136'
        }

        main_layout = QVBoxLayout()
        button_layout = QGridLayout()
        positions = [(i, j) for i in range(3) for j in range(2)]

        for position, (emotion, color) in zip(positions, self.emotion_colors.items()):
            button = QPushButton(emotion)
            from PyQt6.QtWidgets import QSizePolicy
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            button.setStyleSheet(f"""
                QPushButton {{ font-size: 128px; font-weight: bold; padding: 10px; color: {color}; }}
            """)
            button.clicked.connect(lambda checked, emo=emotion: self.log_emotion(emo))
            button_layout.addWidget(button, *position)

        log_label = QLabel('기록된 감정 로그:')
        log_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("font-size: 14px;")
        self.log_display.setMaximumHeight(80)

        action_button_layout = QHBoxLayout()
        self.clear_button = QPushButton('로그 초기화 🗑️')
        self.clear_button.setStyleSheet("font-size: 14px; padding: 8px;")
        self.clear_button.clicked.connect(self.clear_logs)

        self.undo_button = QPushButton('실행 취소 ↩️')
        self.undo_button.setStyleSheet("font-size: 14px; padding: 8px;")
        self.undo_button.clicked.connect(self.undo_last_log)

        self.export_button = QPushButton('CSV로 내보내기 💾')
        self.export_button.setStyleSheet("font-size: 14px; padding: 8px;")
        self.export_button.clicked.connect(self.export_to_csv)

        action_button_layout.addWidget(self.clear_button)
        action_button_layout.addWidget(self.export_button)
        action_button_layout.addWidget(self.undo_button)

        main_layout.addLayout(button_layout, 2)
        main_layout.addWidget(log_label)
        main_layout.addWidget(self.log_display, 1)
        main_layout.addLayout(action_button_layout)

        self.timer_label = QLabel(f"다음 알림까지: {self.remaining_time}초")
        self.timer_label.setStyleSheet("margin-top: 5px; color: grey;")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.timer_label)

        self.setLayout(main_layout)
        self.load_logs()

        # 10초마다 팝업을 띄우는 메인 타이머
        self.reminder_timer = QTimer(self)
        self.reminder_timer.setInterval(10000)
        self.reminder_timer.timeout.connect(self.show_reminder_popup)
        self.reminder_timer.start()

        # 1초마다 라벨을 업데이트하는 카운트다운 타이머
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(1000)
        self.update_timer.timeout.connect(self.update_countdown_label)
        self.update_timer.start()

    def update_countdown_label(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
        self.timer_label.setText(f"다음 알림까지: {self.remaining_time}초")

    def show_reminder_popup(self):
        QApplication.beep() # 알림음 발생

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText("주기적인 감정 기록 시간입니다!!!")
        msg_box.setWindowTitle("감정 기록 알림")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        
        # 팝업 후 타이머 초기화
        self.remaining_time = 10
        self.timer_label.setText(f"다음 알림까지: {self.remaining_time}초")

    def log_emotion(self, emotion):
        timestamp = int(time.time())
        try:
            with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, emotion])
        except IOError as e:
            self.log_display.append(f"파일 쓰기 오류: {e}")
            return
            
        # [개선] 감정 기록 시 타이머를 10초로 초기화
        self.remaining_time = 10 
        self.timer_label.setText(f"다음 알림까지: {self.remaining_time}초")
        
        self.load_logs()

    def load_logs(self):
        if not os.path.exists(self.log_file):
            self.log_display.setText("로그 파일이 없습니다. 첫 감정을 기록해보세요!")
            return
        self.log_display.clear()
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                logs = list(reader)
                # 로그를 역순으로 표시 (최신순)
                for row in reversed(logs):
                    if len(row) == 2:
                        timestamp, emotion = row
                        readable_time = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
                        log_entry = f"[{readable_time}] 감정 기록: {emotion}"
                        self.log_display.append(log_entry)
        except (IOError, ValueError) as e:
            self.log_display.append(f"로그 파일 읽기 오류: {e}")
        # 스크롤을 맨 위로 이동
        self.log_display.verticalScrollBar().setValue(0)

    def export_to_csv(self):
        if not os.path.exists(self.log_file):
            self.log_display.append("내보낼 로그 파일이 없습니다.")
            return
        options = QFileDialog.Option.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(self, "CSV 파일로 저장", f"emotion_log_{int(time.time())}.csv", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_path:
            try:
                with open(self.log_file, 'r', encoding='utf-8') as src, open(file_path, 'w', newline='', encoding='utf-8') as dst:
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
        reply = QMessageBox.question(self, '로그 초기화 확인', '정말로 모든 감정 기록을 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(self.log_file)
                self.log_display.setText("모든 로그가 초기화되었습니다.")
            except OSError as e:
                self.log_display.setText(f"파일 삭제 중 오류 발생: {e}")

    def undo_last_log(self):
        if not os.path.exists(self.log_file) or os.path.getsize(self.log_file) == 0:
            self.log_display.append("\n>> 되돌릴 로그가 없습니다.")
            return
        try:
            with open(self.log_file, 'r', newline='', encoding='utf-8') as f:
                logs = list(csv.reader(f))
            if logs:
                logs.pop()
            else:
                self.log_display.append("\n>> 로그가 비어있습니다.")
                return
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(logs)
            self.load_logs()
            self.log_display.append("\n>> 마지막 로그를 삭제했습니다.")
        except (IOError, IndexError) as e:
            self.log_display.append(f"\n>> 실행 취소 중 오류 발생: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EmotionLogger()
    window.show()
    sys.exit(app.exec())