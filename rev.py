import numpy as np
import wave
from scipy.fft import fft

def wave_to_text(filename="output.wav", freq1=500, freq2=10000, duration=0.1):
    with wave.open(filename, 'r') as f:
        frames = f.readframes(f.getnframes())
        sample_rate = f.getframerate()
        audio = np.frombuffer(frames, dtype=np.int16) / 32767.0

    # 每段音频的长度
    chunk_size = int(sample_rate * duration)
    binary = ''

    for i in range(0, len(audio), chunk_size):
        chunk = audio[i:i + chunk_size]
        spectrum = np.abs(fft(chunk))[:chunk_size // 2]
        freqs = np.fft.fftfreq(len(spectrum), 1 / sample_rate)[:chunk_size // 2]

        # 找到主频率
        dominant_freq = freqs[np.argmax(spectrum)]

        if abs(dominant_freq - freq1) < abs(dominant_freq - freq2):
            binary += '0'
        else:
            binary += '1'

    # 二进制转换为文本
    text = ''.join(chr(int(binary[i:i + 8], 2)) for i in range(0, len(binary), 8))
    return text

# 示例：解析生成的音频
print("解码结果:", wave_to_text())