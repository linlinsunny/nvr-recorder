import sys
import threading
import subprocess
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QCheckBox, QTimeEdit, QSpinBox)
from PyQt5.QtCore import QTimer, QTime, QDateTime
from PyQt5.QtGui import QImage, QPixmap
import cv2

class NVRRecorder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('网络摄像机录像工具')
        self.rtsp_url = 'rtsp://admin:BenBenxin1212@192.168.31.211:554//cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif'
        self.is_previewing = False
        self.is_recording = False
        self.ffmpeg_process = None
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        # 定时检测
        self.schedule_timer = QTimer()
        self.schedule_timer.timeout.connect(self.check_schedule)
        self.schedule_timer.start(10000)  # 每10秒检查一次
        self.duration_timer = None
        self.current_lang = 'zh'
        self.update_language()

    def init_ui(self):
        # 输入区
        self.ip_input = QLineEdit('192.168.31.211')
        self.port_input = QLineEdit('554')
        self.user_input = QLineEdit('admin')
        self.pwd_input = QLineEdit('BenBenxin1212')
        self.pwd_input.setEchoMode(QLineEdit.Password)
        self.protocol_input = QLineEdit('rtsp')
        self.stream_input = QLineEdit('/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')

        # 预览区
        self.preview_label = QLabel('未开启预览')
        self.preview_label.setFixedSize(640, 360)
        self.preview_label.setStyleSheet('background: #222; color: #fff;')

        # 控件区
        self.preview_btn = QPushButton('开启预览')
        self.preview_btn.clicked.connect(self.toggle_preview)
        self.record_btn = QPushButton('开始录像')
        self.record_btn.clicked.connect(self.toggle_record)
        self.record_btn.setEnabled(True)

        # 定时录像设置
        self.timer_checkbox = QCheckBox('定时录像')
        self.start_time_edit = QTimeEdit(QTime(0, 0))
        self.end_time_edit = QTimeEdit(QTime(23, 59))
        self.timer_checkbox.stateChanged.connect(self.on_timer_checkbox)
        # 时长录像设置
        self.duration_checkbox = QCheckBox('时长录像')
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 24)
        self.duration_spin.setSuffix(' 小时')
        self.duration_checkbox.stateChanged.connect(self.on_duration_checkbox)

        # 语言切换按钮
        self.lang_btn = QPushButton('English')
        self.lang_btn.clicked.connect(self.toggle_language)

        # 标签
        self.label_ip = QLabel('IP:')
        self.label_port = QLabel('端口:')
        self.label_user = QLabel('用户名:')
        self.label_pwd = QLabel('密码:')
        self.label_protocol = QLabel('协议:')
        self.label_stream = QLabel('流:')

        # 输入布局
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.label_ip)
        input_layout.addWidget(self.ip_input)
        input_layout.addWidget(self.label_port)
        input_layout.addWidget(self.port_input)
        input_layout.addWidget(self.label_user)
        input_layout.addWidget(self.user_input)
        input_layout.addWidget(self.label_pwd)
        input_layout.addWidget(self.pwd_input)
        input_layout.addWidget(self.label_protocol)
        input_layout.addWidget(self.protocol_input)
        input_layout.addWidget(self.label_stream)
        input_layout.addWidget(self.stream_input)

        # 定时/时长布局
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.timer_checkbox)
        time_layout.addWidget(QLabel('开始'))
        time_layout.addWidget(self.start_time_edit)
        time_layout.addWidget(QLabel('结束'))
        time_layout.addWidget(self.end_time_edit)
        time_layout.addWidget(self.duration_checkbox)
        time_layout.addWidget(self.duration_spin)

        # 主布局
        layout = QVBoxLayout()
        layout.addLayout(input_layout)
        layout.addWidget(self.preview_label)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.preview_btn)
        btn_layout.addWidget(self.record_btn)
        btn_layout.addWidget(self.lang_btn)
        layout.addLayout(btn_layout)
        layout.addLayout(time_layout)
        self.setLayout(layout)

    def get_rtsp_url(self):
        ip = self.ip_input.text().strip()
        port = self.port_input.text().strip()
        user = self.user_input.text().strip()
        pwd = self.pwd_input.text().strip()
        protocol = self.protocol_input.text().strip()
        stream = self.stream_input.text().strip()
        return f"{protocol}://{user}:{pwd}@{ip}:{port}{stream}"

    def toggle_preview(self):
        if not self.is_previewing:
            self.is_previewing = True
            self.preview_btn.setText('关闭预览' if self.current_lang == 'zh' else 'Stop Preview')
            self.cap = cv2.VideoCapture(self.get_rtsp_url())
            self.timer.start(30)
        else:
            self.is_previewing = False
            self.preview_btn.setText('开启预览' if self.current_lang == 'zh' else 'Start Preview')
            self.timer.stop()
            if hasattr(self, 'cap'):
                self.cap.release()
            self.preview_label.setText('未开启预览' if self.current_lang == 'zh' else 'Preview Off')
            self.preview_label.setPixmap(QPixmap())

    def update_frame(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                bytes_per_line = ch * w
                img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                # 适应label大小，显示完整画面
                scaled_img = img.scaled(self.preview_label.width(), self.preview_label.height(), aspectRatioMode=1)
                self.preview_label.setPixmap(QPixmap.fromImage(scaled_img))
            else:
                self.preview_label.setText('视频流中断')

    def on_timer_checkbox(self):
        checked = self.timer_checkbox.isChecked()
        self.start_time_edit.setEnabled(checked)
        self.end_time_edit.setEnabled(checked)

    def on_duration_checkbox(self):
        checked = self.duration_checkbox.isChecked()
        self.duration_spin.setEnabled(checked)

    def toggle_record(self):
        if self.is_recording:
            self.is_recording = False
            self.record_btn.setText('开始录像')
            if self.ffmpeg_process:
                self.ffmpeg_process.terminate()
                self.ffmpeg_process = None
            if self.duration_timer:
                self.duration_timer.stop()
                self.duration_timer = None
        else:
            self.is_recording = True
            self.record_btn.setText('录制中...')
            threading.Thread(target=self.start_recording, daemon=True).start()
            # 时长录像
            if self.duration_checkbox.isChecked():
                hours = self.duration_spin.value()
                self.duration_timer = QTimer()
                self.duration_timer.setSingleShot(True)
                self.duration_timer.timeout.connect(self.toggle_record)
                self.duration_timer.start(hours * 3600 * 1000)

    def start_recording(self):
        url = self.get_rtsp_url()
        now = QDateTime.currentDateTime().toString('yyyyMMdd_HHmmss')
        output_file = f'record_{now}.mp4'
        # ffmpeg 命令，录制音视频，转码保证兼容性
        cmd = [
            'ffmpeg', '-y', '-rtsp_transport', 'tcp', '-i', url,
            '-c:v', 'libx264', '-preset', 'veryfast', '-c:a', 'aac', '-f', 'mp4', output_file
        ]
        self.ffmpeg_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.ffmpeg_process.wait()
        self.is_recording = False
        self.record_btn.setText('开始录像')

    def check_schedule(self):
        if self.timer_checkbox.isChecked():
            now = QTime.currentTime()
            start = self.start_time_edit.time()
            end = self.end_time_edit.time()
            if start <= now <= end:
                if not self.is_recording:
                    self.toggle_record()
            else:
                if self.is_recording:
                    self.toggle_record()

    def toggle_language(self):
        self.current_lang = 'en' if self.current_lang == 'zh' else 'zh'
        self.update_language()

    def update_language(self):
        if self.current_lang == 'zh':
            self.setWindowTitle('网络摄像机录像工具')
            self.preview_btn.setText('开启预览' if not self.is_previewing else '关闭预览')
            self.record_btn.setText('开始录像' if not self.is_recording else '录制中...')
            self.lang_btn.setText('English')
            self.timer_checkbox.setText('定时录像')
            self.duration_checkbox.setText('时长录像')
            self.label_ip.setText('IP:')
            self.label_port.setText('端口:')
            self.label_user.setText('用户名:')
            self.label_pwd.setText('密码:')
            self.label_protocol.setText('协议:')
            self.label_stream.setText('流:')
        else:
            self.setWindowTitle('IP Camera Recorder')
            self.preview_btn.setText('Start Preview' if not self.is_previewing else 'Stop Preview')
            self.record_btn.setText('Start Recording' if not self.is_recording else 'Recording...')
            self.lang_btn.setText('中文')
            self.timer_checkbox.setText('Scheduled Recording')
            self.duration_checkbox.setText('Duration Recording')
            self.label_ip.setText('IP:')
            self.label_port.setText('Port:')
            self.label_user.setText('User:')
            self.label_pwd.setText('Password:')
            self.label_protocol.setText('Protocol:')
            self.label_stream.setText('Stream:')

    def closeEvent(self, event):
        if self.is_previewing:
            self.toggle_preview()
        if self.is_recording and self.ffmpeg_process:
            self.ffmpeg_process.terminate()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = NVRRecorder()
    win.show()
    # 启动后不自动录像，按钮为“开始录像”
    sys.exit(app.exec_())
