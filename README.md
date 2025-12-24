#SyncTalk Voice Cloning Demo
20组（个人）
周苓萱成员
语音克隆模块项目提交

##1. 项目简介
本项目基于 OpenVoice V2 实现中文语音克隆任务。
系统输入为 文本内容 + 参考音频，输出为 保留目标音色特征的合成语音。
本项目聚焦于语音克隆推理与工程封装验证。
实时对话（ASR + LLM + TTS）属于系统级扩展方向，已在架构设计中预留接口（backend/chat_engine.py），但未作为本次实验的强制实现目标。

##2. 实验模式说明
本实验采用 语音克隆模式（Voice Cloning）：
输入：文本（Text），参考音频（Reference Audio）
输出：目标音色的合成语音（WAV）

##3. 项目运行方式（Docker）
Docker 镜像基于 Python 3.9-slim 构建，仅包含推理所需的最小依赖（ffmpeg、sox 等），确保在 CPU 环境下的稳定复现
Docker 镜像的默认入口为：
python infer.py --text "你好，这是音色克隆测试" --ref_audio test.wav --out_dir ./output
3.1 构建镜像
docker build -t synctalk-demo .
3.2 运行推理
docker run --rm synctalk-demo
运行完成后，生成的语音文件位于容器内：/workspace/output/

##4. 推理流程说明
系统内部流程如下：
   参考音频处理
   使用 VAD 提取有效语音段
   获取目标音色特征表示
   文本处理
   中文文本分句与分词
   使用多语言 BERT 提取文本表示
   语音合成（TTS）
   使用 MeloTTS 中文模型生成基础语音
   音色转换（Voice Conversion）
   通过 OpenVoice V2 Converter 将基础语音转换为目标音色
   结果保存
   输出 .wav 文件至 output/ 目录

##5. 实验结果示例
本实验成功生成音色克隆语音文件，例如：
output/cloned_20251220_211027.wav
文件格式：WAV
内容：与参考音频音色一致的中文语音
推理过程无中断错误

##6. 关于评价指标说明（简化实现）
本实验主要验证语音克隆推理的工程可复现性。
由于 NIQE / FID / LSE-C / LSE-D 依赖视频对齐或旧版 CUDA，在当前 CPU Docker 环境中未作为强制运行项,但保留了相应接口作为后续扩展。

本项目提供：
- 推理结果音频（WAV）
- 输出路径与日志可复现

##7. 环境说明
(1) 软件环境
   操作系统：Windows 10，OS: Linux (Docker)
   Python 版本：3.9（Conda 虚拟环境 tfg）
   深度学习框架：
      PyTorch
      语音相关工具：OpenVoice V2，
      MeloTTS（中文语音合成），
      librosa，
      ffmpeg（用于音视频处理，ffmpeg: 已在镜像中预装）
(2) 硬件环境
   推理设备：CPU（本次实验未使用 GPU）


##8. 附录: 实验部署时遇到的困难和解决方案,供复现时参考
# OpenVoice 音色克隆使用说明

## 功能说明

## 快速开始

### 1. 安装依赖

```bash
pip install torch librosa soundfile numpy
```

### 2. 安装 OpenVoice

#### 方式1:从 GitHub 克隆并安装

**Windows 用户注意**：如果遇到 `av` 包编译错误，请使用以下方法之一：

**使用 conda（推荐，避免编译问题）**
```bash
# 使用 conda 创建环境（conda 提供预编译的包）
conda create -n openvoice python=3.9
conda activate openvoice
conda install -c conda-forge av  # 安装预编译的 av 包
cd OpenVoice
pip install -e . --no-deps  # 先不安装依赖
pip install -r requirements.txt  # 手动安装依赖
```
```
#### 方式2：下载模型文件（本实验使用该方法）

**OpenVoice V2（支持更多语言）：**

下载模型文件：
- 下载地址：https://myshell-public-repo-host.s3.amazonaws.com/openvoice/checkpoints_v2_0417.zip
- 下载后解压到 `OpenVoice/checkpoints_v2/` 目录

然后安装 MeloTTS（V2 需要）：
```bash
pip install git+https://github.com/myshell-ai/MeloTTS.git
python -m unidic download
```

### 3. 运行音色克隆

使用 test.wav 作为参考音频进行音色克隆：

```bash
python infer.py --text "你好，这是音色克隆测试" --ref_audio test.wav --out_dir ./output
```

或者使用 `--audio` 参数（会自动将其作为参考音频）：

```bash
python infer.py --text "你好，这是音色克隆测试" --audio test.wav --out_dir ./output
```

## 参数说明

- `--text`: 要合成的文本内容（必需）
- `--ref_audio` 或 `--audio`: 参考音频文件路径（用于提取音色）
- `--out_dir`: 输出目录（默认：./output）
- `--out_filename`: 输出文件名（可选，不指定则自动生成）

## 输出

生成的音频文件会保存在指定的输出目录中，文件名格式为 `cloned_YYYYMMDD_HHMMSS.wav`

## 故障排除

### 问题1：安装时出现 `av` 包编译错误

**错误信息**：`ERROR: Failed to build 'av' when getting requirements to build wheel`
本项目已集成 OpenVoice 音色克隆功能，可以使用参考音频（test.wav）克隆说话人的音色，生成指定文本的语音。
在 Windows 上安装 OpenVoice 时，可能会遇到 `av` 包编译错误：
```
ERROR: Failed to build 'av' when getting requirements to build wheel
```
这是因为 `av` (PyAV) 需要 C 编译器来编译，而 Windows 默认没有。

**解决方案**：

1. **使用 conda 安装 av**（最简单）：
   ```bash
   conda install -c conda-forge av
   ```

2. **跳过 av 包**（通常不影响核心功能）：
   ```bash
   pip install -e . --no-deps
   pip install -r requirements.txt  # 手动安装，遇到 av 错误时按 Ctrl+C 跳过
   ```

3. **使用预编译包**：
   ```bash
   pip install av --only-binary :all:
   ```

### 问题2：其他依赖安装错误

如果遇到其他包的版本冲突，可以：
- 使用 conda 环境隔离依赖
- 或者逐个安装依赖，跳过有问题的包

## 注意事项

1. **参考音频要求**：
   - 清晰的单声道音频
   - 采样率建议 16kHz 或 24kHz
   - 时长约 3-5 秒，质量越好效果越好
   - 建议使用清晰的说话声，无背景噪音

2. **系统要求**：
   - Python 3.9+
   - Windows 用户建议使用 conda 环境避免编译问题
   - 如果使用 CUDA，确保已安装 PyTorch GPU 版本
   - 首次运行会加载模型，可能需要一些时间

3. **模型选择**：
   - OpenVoice V1：适合中文和基础使用
   - OpenVoice V2：支持更多语言（英语、西班牙语、法语、中文、日语、韩语），需要额外安装 MeloTTS

## 推荐配置

对于 Windows 用户，最推荐的配置是：

1. **使用 conda 环境**：避免编译问题
2. **使用 Python 3.9**：与 OpenVoice 兼容性最好
3. **使用 OpenVoice V1**：更简单，依赖更少

```bash
# 完整安装流程
conda create -n openvoice python=3.9
conda activate openvoice
conda install -c conda-forge av librosa soundfile
cd OpenVoice
pip install -e . --no-deps
pip install faster-whisper pydub wavmark numpy
pip install eng_to_ipa inflect unidecode whisper-timestamped
pip install pypinyin cn2an jieba gradio langid
```

## 如果仍然遇到问题

1. 检查 Python 版本：`python --version`（应该是 3.9+）
2. 更新 pip：`python -m pip install --upgrade pip`
3. 使用虚拟环境隔离：`python -m venv venv`
4. 查看具体错误信息，搜索解决方案

# Windows 安装 ffmpeg 指南
## 方法1：使用 Conda（最简单，强烈推荐，本实验使用这种方法）
```powershell
conda install -c conda-forge ffmpeg
```
可以直接在 conda 环境中使用 ffmpeg，无需配置 PATH。

## 方法2：手动下载并配置 PATH(本项目也尝试过)
### 步骤1：下载 ffmpeg

1. 访问：https://www.gyan.dev/ffmpeg/builds/
2. 点击 "Download Build" 按钮
3. 选择 "ffmpeg-release-essentials.zip" 下载

### 步骤2：解压文件

1. 将下载的 zip 文件解压到某个目录，例如：
   - `C:\ffmpeg`
   - 或 `C:\Program Files\ffmpeg`
   - 或 `D:\Tools\ffmpeg`

2. 解压后，应该看到以下目录结构：
   ```
   ffmpeg/
   ├── bin/
   │   ├── ffmpeg.exe
   │   ├── ffplay.exe
   │   └── ffprobe.exe
   ├── doc/
   └── ...
   ```
### 步骤3：添加到 PATH 环境变量

## 常见问题

### Q: 添加后仍然找不到 ffmpeg？

A: 
1. 确保关闭了所有终端窗口并重新打开
2. 检查路径是否正确（注意是 `bin` 目录，不是 `ffmpeg` 根目录）
3. 在 PowerShell 中运行 `$env:Path` 查看当前 PATH，确认你的路径已添加

### Q: 使用 conda 还是手动安装？

A: 
- **Conda**：更简单，只影响当前环境，不会污染系统环境
- **手动安装**：全局可用，但需要配置 PATH

如果你使用的是 conda 环境，**强烈推荐使用 conda 安装**。



