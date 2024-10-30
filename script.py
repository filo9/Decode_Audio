import numpy as np
import pyaudio
from scipy.fft import fft
import time

def detect_frequency(chunk, sample_rate):
    """检测主频率"""
    spectrum = np.abs(fft(chunk))[:len(chunk) // 2]
    freqs = np.fft.fftfreq(len(spectrum), 1 / sample_rate)[:len(chunk) // 2]
    return freqs[np.argmax(spectrum)]

def record_audio_on_signal(start_freq=500, end_freq=250, sample_rate=44100, duration=0.5, timeout=5):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, input=True, frames_per_buffer=1024)
    frames = []
    recording = False
    start_time = None

    while True:
        data = stream.read(1024)
        audio_chunk = np.frombuffer(data, dtype=np.int16)

        # 检测频率
        dominant_freq = detect_frequency(audio_chunk, sample_rate)

        # 检测开始标志，需持续检测一段时间
        if not recording and abs(dominant_freq - start_freq) < 50:
            # 额外验证，连续检测到多次启动频率才正式开始录音
            start_detection_time = time.time()
            consecutive_detection = 0
            while time.time() - start_detection_time < 0.5:  # 持续检测500毫秒
                data = stream.read(1024)
                audio_chunk = np.frombuffer(data, dtype=np.int16)
                dominant_freq = detect_frequency(audio_chunk, sample_rate)
                if abs(dominant_freq - start_freq) < 50:
                    consecutive_detection += 1
                else:
                    consecutive_detection = 0
                if consecutive_detection > 3:  # 连续多次检测到
                    recording = True
                    start_time = time.time()  # 开始录音计时
                    print("检测到开始标志，开始录音")
                    break

        # 若已开始录音，将数据添加到 frames
        if recording:
            frames.append(data)

        # 检测到结束标志或超时，加入最小录音时间检测
        if recording and time.time() - start_time > 0.5:  # 确保至少录音0.5秒
            if abs(dominant_freq - end_freq) < 50 or time.time() - start_time > timeout:
                print("检测到结束标志或超时，停止录音")
                break

    stream.stop_stream()
    stream.close()
    p.terminate()

    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
    return audio_data, sample_rate

def decode_audio(audio_data, sample_rate, freq0=400, freq1=3000, duration=0.5):
    chunk_size = int(sample_rate * duration)
    binary = ''
    threshold_value = 500  # 阈值，用于过滤噪声

    for i in range(0, len(audio_data), chunk_size):
        chunk = audio_data[i:i + chunk_size]
        if len(chunk) == 0:
            continue

        spectrum = np.abs(fft(chunk))[:chunk_size // 2]
        freqs = np.fft.fftfreq(len(spectrum), 1 / sample_rate)[:chunk_size // 2]

        if np.max(spectrum) > threshold_value:
            dominant_freq = freqs[np.argmax(spectrum)]
            if abs(dominant_freq - freq0) < abs(dominant_freq - freq1):
                binary += '0'
            else:
                binary += '1'

    # 查找起始和结束标志
    start_index = binary.find('00100011')  # '#' 的二进制代码
    end_index = binary.rfind('00100011')

    # 确保数据在起始和结束标志之间
    if start_index != -1 and end_index != -1 and end_index > start_index:
        data_binary = binary[start_index + 8:end_index]
    else:
        data_binary = binary  # 若未找到标志则直接尝试解码

    # 二进制转文本
    text = ""
    for i in range(0, len(data_binary), 8):
        byte = data_binary[i:i + 8]
        if len(byte) == 8:
            try:
                char = chr(int(byte, 2))
                if 32 <= ord(char) <= 126:
                    text += char
            except ValueError:
                continue
    return text

# 主程序：检测到启动信号后开始录音
audio_data, sample_rate = record_audio_on_signal()
decoded_text = decode_audio(audio_data, sample_rate)
print("接收到wifi:", decoded_text)