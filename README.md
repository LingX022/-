# SyncTalk Voice Cloning Demo

**第 20 组（个人）**
**周苓萱成员**
**语音克隆模块项目提交**


## 1. 项目简介

本项目基于 **OpenVoice V2** 实现中文语音克隆（Voice Cloning）任务。

* **输入**：文本内容（Text） + 参考音频（Reference Audio）
* **输出**：保留目标音色特征的合成语音（WAV）

本实验聚焦于**语音克隆推理流程与工程封装的可复现性验证**。

> 说明：
> 实时对话（ASR + LLM + TTS）属于系统级扩展方向，已在架构设计中预留接口
> （`backend/chat_engine.py`），但未作为本次实验的强制实现目标。

---

## 2. 实验模式说明

本实验采用 **语音克隆模式（Voice Cloning）**：

* **输入**：

  * 文本（Text）
  * 参考音频（Reference Audio）
* **输出**：

  * 目标音色的合成语音（WAV）

---

## 3. 项目运行方式（Docker）

本项目提供 **Docker 化推理环境**，用于验证在 CPU 环境下的稳定复现能力。

### 3.1 Docker 环境说明

* 基础镜像：Python 3.9-slim
* 仅包含推理所需的最小依赖：

  * ffmpeg
  * sox
  * OpenVoice V2
  * MeloTTS
* **无需 GPU**

Docker 镜像默认入口命令为：

```bash
python infer.py \
  --text "你好，这是音色克隆测试" \
  --ref_audio test.wav \
  --out_dir ./output
```

---

### 3.2 构建镜像

```bash
docker build -t synctalk-demo .
```

---

### 3.3 运行推理

```bash
docker run --rm synctalk-demo
```

运行完成后，生成的语音文件位于容器内：

```
/workspace/output/
```

---

## 4. 推理流程说明

系统内部推理流程如下：

1. **参考音频处理**

   * 使用 VAD 提取有效语音段
   * 获取目标音色特征表示

2. **文本处理**

   * 中文文本分句与分词
   * 使用多语言 BERT 提取文本表示

3. **语音合成（TTS）**

   * 使用 MeloTTS 中文模型生成基础语音

4. **音色转换（Voice Conversion）**

   * 通过 OpenVoice V2 Converter 将基础语音转换为目标音色

5. **结果保存**

   * 输出 `.wav` 文件至 `output/` 目录

---

## 5. 实验结果示例

实验成功生成音色克隆语音文件，例如：

```
output/cloned_20251220_211027.wav
```

* 文件格式：WAV
* 内容：与参考音频音色一致的中文语音
* 推理过程：无中断错误

---

## 6. 评价指标说明（简化实现）

本实验主要验证：

* 语音克隆推理流程的工程完整性
* Docker 环境下的可复现性

由于以下指标依赖视频对齐或旧版 CUDA 环境：

* NIQE
* FID
* LSE-C / LSE-D

在当前 **CPU Docker 环境** 中未作为强制运行项，但已保留接口用于后续扩展。

**本项目最终提供：**

* 可复现的推理音频（WAV）
* 明确的输出路径
* 可追溯的运行日志

---

## 7. 实验环境说明

### 7.1 软件环境

* 操作系统：

  * Windows 10（本地）
  * Linux（Docker）
* Python：3.9
* 深度学习与语音工具：

  * PyTorch
  * OpenVoice V2
  * MeloTTS
  * librosa
  * ffmpeg（已在 Docker 镜像中预装）

---

### 7.2 硬件环境

* 推理设备：CPU
* 本实验未使用 GPU

---

## 8. 附录：部署过程中的问题与解决方案（供复现参考）

### 8.1 OpenVoice 音色克隆使用说明

#### 功能说明

本项目已集成 OpenVoice 音色克隆功能，可基于参考音频生成指定文本的目标音色语音。

---

### 8.2 快速开始（非 Docker）

#### 1. 安装基础依赖

```bash
pip install torch librosa soundfile numpy
```

---

#### 2. 安装 OpenVoice

##### 方式一：从 GitHub 克隆并安装（Windows 用户注意）

Windows 下若遇到 `av` 包编译错误，推荐使用 conda 安装：

```bash
conda create -n openvoice python=3.9
conda activate openvoice
conda install -c conda-forge av
cd OpenVoice
pip install -e . --no-deps
pip install -r requirements.txt
```

---

##### 方式二：下载模型文件（本实验采用）

* 下载地址：
  [https://myshell-public-repo-host.s3.amazonaws.com/openvoice/checkpoints_v2_0417.zip](https://myshell-public-repo-host.s3.amazonaws.com/openvoice/checkpoints_v2_0417.zip)
* 解压至：

  ```
  OpenVoice/checkpoints_v2/
  ```

安装 MeloTTS：

```bash
pip install git+https://github.com/myshell-ai/MeloTTS.git
python -m unidic download
```

---

### 8.3 运行音色克隆

```bash
python infer.py \
  --text "你好，这是音色克隆测试" \
  --ref_audio test.wav \
  --out_dir ./output
```

或：

```bash
python infer.py \
  --text "你好，这是音色克隆测试" \
  --audio test.wav \
  --out_dir ./output
```

---

### 8.4 输出说明

* 默认输出目录：`./output`
* 文件命名格式：

  ```
  cloned_YYYYMMDD_HHMMSS.wav
  ```

---

### 8.5 常见问题：`av` 包安装失败

**错误信息：**

```
ERROR: Failed to build 'av' when getting requirements to build wheel
```

**解决方案：**

1. 使用 conda：

   ```bash
   conda install -c conda-forge av
   ```

2. 使用二进制包：

   ```bash
   pip install av --only-binary :all:
   ```

3. 跳过 av（通常不影响核心推理）：

   ```bash
   pip install -e . --no-deps
   pip install -r requirements.txt
   ```

---

## 9. Windows 下 ffmpeg 安装说明（补充）

### 方法一（推荐）：使用 conda

```powershell
conda install -c conda-forge ffmpeg
```

无需配置 PATH，仅作用于当前环境。

---

### 方法二：手动安装并配置 PATH

1. 下载：[https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
2. 解压后确认：

   ```
   ffmpeg/bin/ffmpeg.exe
   ```
3. 将 `bin` 目录加入系统 PATH

---



