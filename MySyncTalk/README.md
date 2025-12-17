20组（个人）
周苓萱 成员
基于语音克隆的实时对话语音生成模块

# MySyncTalk

## 简介
本项目为 SyncTalk 的复现与简化实现，用于 Talking Face Generation 场景，
主要负责语音输入后的推理接口封装与前端对接。

## 目录结构
- inference.py：模型推理代码
- service.py：后端服务接口
- README.md：说明文档

## 使用说明
1. 系统前端提交音频请求
2. 后端调用 service.py 中的 handle_request
3. inference.py 执行模型推理并返回生成结果路径

## 当前状态
- 已完成基础推理接口封装
- 可与系统前端正常对接
- 后续可替换为完整 SyncTalk 模型推理逻辑
