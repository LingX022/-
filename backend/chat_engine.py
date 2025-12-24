import os
import speech_recognition as sr
from zhipuai import ZhipuAI

def chat_response(data):
    """
    实时对话系统视频生成逻辑。
    """
    print("[backend.chat_engine] 收到数据：")
    for k, v in data.items():
        print(f"  {k}: {v}")

    # 确保目录存在
    os.makedirs("./static/audios", exist_ok=True)
    os.makedirs("./static/text", exist_ok=True)
    os.makedirs("./static/videos", exist_ok=True)
    os.makedirs("./output", exist_ok=True)

    # 获取数据参数
    model_name = data.get("model_name", "default")
    model_param = data.get("model_param", "")
    voice_clone = data.get("voice_clone", "default")
    api_choice = data.get("api_choice", "glm-4-plus")

    # 1. 语音转文字
    input_audio = "./static/audios/input.wav"
    input_text = "./static/text/input.txt"
    
    # 检查前端上传的音频文件是否存在
    if os.path.exists("./static/audios/input.wav"):
        print("使用前端上传的音频文件")
        input_audio = "./static/audios/input.wav"
    elif os.path.exists("./SyncTalk/audio/aud.wav"):
        print("使用SyncTalk默认音频文件")
        input_audio = "./SyncTalk/audio/aud.wav"
    else:
        print("警告：没有找到音频文件")
        return None
    
    # 执行语音转文字
    recognized_text = audio_to_text(input_audio, input_text)
    
    if not recognized_text:
        print("语音识别失败，无法继续对话")
        return None

    # 2. 大模型回答
    output_text = "./static/text/output.txt"
    api_key = "31af4e1567ad48f49b6d7b914b4145fb.MDVLvMiePGYLRJ7M"
    model = api_choice
    ai_response = get_ai_response(input_text, output_text, api_key, model)
    
    if not ai_response:
        print("获取AI回答失败，无法继续对话")
        return None

    # 3. 文字转语音（使用语音克隆）
    print("正在生成语音回复...")
    
    # 尝试导入并使用MySyncTalk的语音克隆功能
    try:
        import sys
        sys.path.append("../")
        from MySyncTalk.service import handle_request
        
        # 设置默认参考音频（可根据需要修改）
        ref_audio = "./OpenVoice/resources/demo_speaker0.mp3"
        
        # 确保参考音频存在
        if not os.path.exists(ref_audio):
            # 如果默认参考音频不存在，尝试使用其他可用的参考音频
            ref_audio = next((f for f in os.listdir("./OpenVoice/resources/") if f.endswith(".mp3")), None)
            if ref_audio:
                ref_audio = f"./OpenVoice/resources/{ref_audio}"
        
        if ref_audio and os.path.exists(ref_audio):
            print(f"使用参考音频: {ref_audio}")
            # 使用语音克隆生成语音
            tts_output = handle_request(
                text=ai_response,
                ref_audio=ref_audio,
                output_dir="./output",
                voice_clone=voice_clone
            )
            print(f"语音生成成功: {tts_output}")
        else:
            print("没有找到参考音频，使用基础文本转语音")
            # 使用基础文本转语音（无克隆）
            tts_output = handle_request(
                text=ai_response,
                output_dir="./output",
                voice_clone=voice_clone
            )
            print(f"语音生成成功: {tts_output}")
            
    except ImportError as e:
        print(f"导入MySyncTalk失败: {e}")
        print("使用备用文本转语音方案")
        # 备用方案：使用edge-tts或其他TTS
        tts_output = _text_to_speech_basic(ai_response, "./output", "response.wav")
    except Exception as e:
        print(f"语音生成失败: {e}")
        return None
    
    # 4. 生成视频（这里可以根据需要添加视频生成逻辑）
    # 目前暂时返回视频路径，实际项目中应整合视频生成功能
    video_path = os.path.join("static", "videos", "chat_response.mp4")
    print(f"[backend.chat_engine] 生成视频路径：{video_path}")
    
    return video_path


def _text_to_speech_basic(text, output_dir, out_filename):
    """基础文本转语音实现（备用方案）"""
    try:
        import edge_tts
        import asyncio
        from datetime import datetime
        
        async def generate_speech():
            communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
            output_file = os.path.join(output_dir, out_filename)
            await communicate.save(output_file)
            return output_file
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        output_file = loop.run_until_complete(generate_speech())
        loop.close()
        
        return output_file
    except Exception as e:
        print(f"基础TTS失败: {e}")
        # 生成占位文件
        output_file = os.path.join(output_dir, out_filename)
        with open(output_file, 'w') as f:
            f.write("语音生成失败")
        return output_file

def audio_to_text(input_audio, input_text):
    try:
        # 确保输入目录存在
        os.makedirs(os.path.dirname(input_text), exist_ok=True)
        
        # 初始化识别器
        recognizer = sr.Recognizer()
        
        # 加载音频文件
        with sr.AudioFile(input_audio) as source:
            # 调整环境噪声
            recognizer.adjust_for_ambient_noise(source)
            # 读取音频数据
            audio_data = recognizer.record(source)
            
            print("正在识别语音...")
            
            # 使用Google语音识别
            text = recognizer.recognize_google(audio_data, language='zh-CN')
            
            # 将结果写入文件
            with open(input_text, 'w', encoding='utf-8') as f:
                f.write(text)
                
            print(f"语音识别完成！结果已保存到: {input_text}")
            print(f"识别结果: {text}")
            
            return text
            
    except sr.UnknownValueError:
        print("无法识别音频内容")
        # 写入默认文本以便后续处理
        with open(input_text, 'w', encoding='utf-8') as f:
            f.write("无法识别的语音内容")
        return "无法识别的语音内容"
    except sr.RequestError as e:
        print(f"语音识别服务错误: {e}")
        # 写入默认文本以便后续处理
        with open(input_text, 'w', encoding='utf-8') as f:
            f.write("语音识别服务错误")
        return "语音识别服务错误"
    except FileNotFoundError:
        print(f"音频文件不存在: {input_audio}")
        # 写入默认文本以便后续处理
        with open(input_text, 'w', encoding='utf-8') as f:
            f.write("音频文件不存在")
        return "音频文件不存在"
    except Exception as e:
        print(f"发生错误: {e}")
        # 写入默认文本以便后续处理
        with open(input_text, 'w', encoding='utf-8') as f:
            f.write(f"发生错误: {str(e)}")
        return f"发生错误: {str(e)}"

def get_ai_response(input_text, output_text, api_key, model):
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_text), exist_ok=True)
        
        # 读取输入文本
        with open(input_text, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            
        if not content:
            print("输入文本为空，无法获取AI回答")
            return "输入文本为空"
        
        print(f"正在获取AI回答，问题: {content}")
        
        # 调用ZhipuAI API
        client = ZhipuAI(api_key = api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": content}]
        )
        
        # 提取回答内容
        output = response.choices[0].message.content
        
        # 保存回答到文件
        with open(output_text, 'w', encoding='utf-8') as file:
            file.write(output)
            
        print(f"答复已保存到: {output_text}")
        print(f"AI回答: {output}")
        
        return output
        
    except FileNotFoundError:
        print(f"输入文件不存在: {input_text}")
        return "输入文件不存在"
    except Exception as e:
        print(f"获取AI回答时发生错误: {e}")
        return f"获取AI回答时发生错误: {str(e)}"