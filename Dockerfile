# SyncTalk Voice Cloning
# 1. 使用官方 Python 基础镜像
FROM python:3.9-slim

# 2. 设置工作目录
WORKDIR /workspace

# 3. 安装系统依赖（ffmpeg 必须）
RUN apt-get update && apt-get install -y\ 
    ffmpeg \
    sox\
    libgl1\
    && rm -rf /var/lib/apt/lists/*

# 4. 复制项目文件到容器
## 先复制 requirements（利用 Docker cache）
COPY requirements.txt /workspace/requirements.txt

# 5. 安装 Python 依赖（不升级 pip，减少不确定性）
RUN pip install --no-cache-dir -r requirements.txt

# 6. 复制项目核心文件
COPY infer.py /workspace/infer.py
COPY test.wav /workspace/test.wav
COPY OpenVoice /workspace/OpenVoice

# 7. 创建输出目录
RUN mkdir -p /workspace/output

# 8. 默认运行命令（语音克隆）
CMD ["python", "infer.py", "--text", "你好，这是音色克隆测试",  "--ref_audio", "test.wav","--out_dir", "output"]
