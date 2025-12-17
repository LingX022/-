# MySyncTalk/service.py
#在这里改逻辑，前端后端都不要动

from .inference import run_inference

def handle_request(audio_path, output_dir):
    """
    后端统一调用入口
    """
    print("[MySyncTalk] Handling request...")
    result = run_inference(audio_path, output_dir)
    return result
