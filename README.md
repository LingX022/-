SyncTalk Voice Cloning Demo
1. 项目简介
本项目基于 OpenVoice V2 实现中文语音克隆任务。
系统输入为 文本内容 + 参考音频，输出为 保留目标音色特征的合成语音。
本项目聚焦于语音克隆推理与工程封装验证。
实时对话（ASR + LLM + TTS）属于系统级扩展方向，已在架构设计中预留接口（backend/chat_engine.py），但未作为本次实验的强制实现目标。

2. 实验模式说明
本实验采用 语音克隆模式（Voice Cloning）：
输入：文本（Text），参考音频（Reference Audio）
输出：目标音色的合成语音（WAV）

3. 项目运行方式（Docker）
Docker 镜像基于 Python 3.9-slim 构建，仅包含推理所需的最小依赖（ffmpeg、sox 等），确保在 CPU 环境下的稳定复现
Docker 镜像的默认入口为：
python infer.py --text "你好，这是音色克隆测试" --ref_audio test.wav --out_dir ./output
3.1 构建镜像
docker build -t synctalk-demo .
3.2 运行推理
docker run --rm synctalk-demo
运行完成后，生成的语音文件位于容器内：/workspace/output/

4. 推理流程说明
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

5. 实验结果示例
本实验成功生成音色克隆语音文件，例如：
output/cloned_20251220_211027.wav
文件格式：WAV
内容：与参考音频音色一致的中文语音
推理过程无中断错误

6. 关于评价指标说明（简化实现）
本实验主要验证语音克隆推理的工程可复现性。
由于 NIQE / FID / LSE-C / LSE-D 依赖视频对齐或旧版 CUDA，在当前 CPU Docker 环境中未作为强制运行项,但保留了相应接口作为后续扩展。

本项目提供：
- 推理结果音频（WAV）
- 输出路径与日志可复现

7. 环境说明
Python: 3.9
OS: Linux (Docker)
推理设备: CPU
ffmpeg: 已在镜像中预装

8. 附录: 实验部署时遇到的困难和解决方案,供复现时参考
