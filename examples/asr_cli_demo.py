import argparse
import soundfile as sf
import numpy as np
import sys
from src.asr.audio_capture import AudioCapture
from src.asr.audio_processor import AudioProcessor
from src.asr.funasr_recognizer import FunASRRecognizer


def record_audio(duration=5, samplerate=16000, channels=1):
    """录音指定秒数，返回音频数据（numpy 数组）"""
    print(f"开始录音 {duration} 秒...")
    audio_capture = AudioCapture(sample_rate=samplerate, channels=channels)
    audio_capture.start()
    audio_data = []
    for _ in range(int(samplerate * duration / audio_capture.chunk_size)):
        chunk = audio_capture.read()
        if chunk is not None:
            audio_data.append(chunk)
    audio_capture.stop()
    print("录音结束。")
    if audio_data:
        return np.concatenate(audio_data, axis=0)
    else:
        return None


def recognize_audio(audio_np, samplerate=16000):
    """调用 ASR 识别"""
    audio_processor = AudioProcessor(sample_rate=samplerate)
    recognizer = FunASRRecognizer()
    processed = audio_processor.preprocess(audio_np)
    text = recognizer.recognize(processed)
    return text


def main():
    parser = argparse.ArgumentParser(description="命令行语音识别 Demo")
    parser.add_argument('--wav', type=str, help='本地 wav 文件路径')
    parser.add_argument('--record', type=int, help='录音秒数（优先使用 wav 文件）')
    args = parser.parse_args()

    if args.wav:
        print(f"读取音频文件: {args.wav}")
        audio_np, sr = sf.read(args.wav)
        if sr != 16000:
            print(f"采样率为 {sr}，将自动重采样到 16kHz")
        text = recognize_audio(audio_np, samplerate=16000)
        print(f"识别结果: {text}")
    elif args.record:
        audio_np = record_audio(duration=args.record)
        if audio_np is not None:
            text = recognize_audio(audio_np, samplerate=16000)
            print(f"识别结果: {text}")
        else:
            print("录音失败，无音频数据。")
    else:
        print("请指定 --wav 文件或 --record 秒数。示例：")
        print("  python examples/asr_cli_demo.py --wav test.wav")
        print("  python examples/asr_cli_demo.py --record 5")

if __name__ == '__main__':
    main() 