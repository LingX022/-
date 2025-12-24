# infer.py
import argparse
import os
import sys

def parse_args():
    parser = argparse.ArgumentParser(
        description="语音克隆推理入口 (文本 -> 语音 或 音频 -> 语音)"
    )
    parser.add_argument(
        "--text",
        type=str,
        default=None,
        help="输入文本（用于文本转语音模式）"
    )
    parser.add_argument(
        "--audio",
        type=str,
        default=None,
        help="输入音频文件路径（用于语音克隆模式）"
    )
    parser.add_argument(
        "--ref_audio",
        type=str,
        default=None,
        help="参考音频文件路径（用于语音克隆，指定目标说话人）。如果使用 --audio，可以将其作为参考音频"
    )
    parser.add_argument(
        "--voice_clone",
        type=str,
        default="default",
        help="语音克隆模型选择 (default, cloneA, cloneB, 或语音名称)"
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default="./output",
        help="输出目录"
    )
    parser.add_argument(
        "--out_filename",
        type=str,
        default=None,
        help="输出文件名（不指定则自动生成）"
    )
    # SyncTalk模式参数（可选）
    parser.add_argument(
        "--model_dir",
        type=str,
        default=None,
        help="SyncTalk模型目录路径（仅在使用SyncTalk模式时需要）"
    )
    parser.add_argument(
        "--gpu",
        type=str,
        default="GPU0",
        help="GPU设备 (GPU0, GPU1, CPU, etc., default: GPU0)"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    text = args.text
    audio_path = args.audio
    ref_audio = args.ref_audio
    voice_clone = args.voice_clone
    out_dir = args.out_dir
    out_filename = args.out_filename
    model_dir = args.model_dir
    gpu = args.gpu

    # 确定运行模式
    use_synctalk = model_dir is not None and audio_path is not None
    use_voice_clone = text is not None or (audio_path is not None and not use_synctalk)

    if not use_synctalk and not use_voice_clone:
        raise ValueError(
            "请指定以下之一：\n"
            "  1. --text <文本> （文本转语音）\n"
            "  2. --audio <音频> --ref_audio <参考音频> （语音克隆）\n"
            "  3. --audio <音频> --model_dir <模型目录> （SyncTalk模式）"
        )

    # SyncTalk模式：需要模型目录
    if use_synctalk:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")
        
        model_dir_abs = os.path.abspath(model_dir)
        
        if not os.path.exists(model_dir_abs):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            syncTalk_model_dir = os.path.join(script_dir, "SyncTalk", "model")
            error_msg = f"SyncTalk模型目录不存在: {model_dir}\n"
            error_msg += f"（绝对路径: {model_dir_abs}）\n"
            
            if os.path.exists(syncTalk_model_dir):
                available_models = [d for d in os.listdir(syncTalk_model_dir) 
                                  if os.path.isdir(os.path.join(syncTalk_model_dir, d))]
                if available_models:
                    error_msg += f"\n可用的模型目录:\n"
                    for model in available_models:
                        error_msg += f"  - {model}\n"
            else:
                error_msg += f"\n提示：如果您只需要语音克隆功能，请使用 --text 或 --audio --ref_audio 参数，\n"
                error_msg += f"而不需要 --model_dir 参数。"
            
            raise FileNotFoundError(error_msg)
        
        model_dir = model_dir_abs
        print("[INFO] 使用 SyncTalk 模式")

    # 语音克隆模式
    else:
        if text is None and audio_path is None:
            raise ValueError("语音克隆模式需要 --text 或 --audio 参数")
        
        print("[INFO] 使用语音克隆模式")

    os.makedirs(out_dir, exist_ok=True)

    try:
        from MySyncTalk.service import handle_request
    except ImportError as e:
        print("[ERROR] 无法导入语音克隆服务")
        raise e

    print("[INFO] 开始语音克隆推理...")
    if text:
        print(f"[INFO] 输入文本: {text}")
    if audio_path:
        print(f"[INFO] 输入音频: {audio_path}")
    if ref_audio:
        print(f"[INFO] 参考音频: {ref_audio}")
    print(f"[INFO] 语音克隆模型: {voice_clone}")
    print(f"[INFO] 输出目录: {out_dir}")

    # 调用服务函数
    if use_synctalk:
        result = handle_request(audio_path, out_dir, model_dir, gpu)
    else:
        result = handle_request(
            audio_path=audio_path,
            output_dir=out_dir,
            text=text,
            ref_audio=ref_audio,
            voice_clone=voice_clone,
            out_filename=out_filename
        )

    print("[INFO] Inference finished.")
    print(f"[INFO] Output file: {result}")
    
    # 转换为绝对路径并显示
    abs_result = os.path.abspath(result)
    print(f"[INFO] 绝对路径: {abs_result}")
    
    # 检查文件是否存在
    if os.path.exists(abs_result):
        print(f"[INFO] ✓ 文件已生成，可以在以下位置找到：")
        print(f"[INFO] {abs_result}")
    else:
        print(f"[WARNING] ⚠ 文件不存在: {abs_result}")
        print(f"[INFO] 请检查推理过程是否正确完成")


if __name__ == "__main__":
    main()
