# Python 网络摄像机录像程序

本项目为一款基于 PyQt5 的网络摄像机录像工具，支持 RTSP 协议，支持音视频录制，支持实时预览开关。

## 功能
- 支持输入摄像机 IP、端口、用户名、密码、协议（RTSP）
- 程序启动后自动录像（视频+音频），默认不显示预览
- 可随时开启/关闭实时预览
- 支持录制视频和音频流

## 依赖
- PyQt5
- opencv-python
- ffmpeg-python
- 需本地安装 ffmpeg（macOS 可用 brew 安装）

## 安装依赖
```bash
pip install -r requirements.txt
```
## 安装 ffmpeg
### windows
https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z
然后加入环境里自己找教程。
或者（基本下载不了需要mf）
choco install ffmpeg 
### mac
brew install ffmpeg
## 运行
```bash
python main.py
```

## 默认摄像机地址
rtsp://用户名:密码@ip:554/stream1

## 乐橙流
/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif
