import numpy as np
import wave
import pyaudio

def text_to_wave(text, filename="output.wav", freq1=500, freq2=10000, duration=0.1):
    # 二进制编码
    binary = ''.join(format(ord(c), '08b') for c in text)

    # 生成音频信号
    sample_rate = 80000  # 采样率
    audio = []

    for bit in binary:
        freq = freq1 if bit == '0' else freq2
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        wave_data = 0.5 * np.sin(2 * np.pi * freq * t)
        audio.extend(wave_data)

    audio = np.array(audio, dtype=np.float32)

    # 保存为WAV文件
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes((audio * 32767).astype(np.int16).tobytes())

    print(f"已生成音频文件: {filename}")

# 示例：将"hello"转换为音频
text_to_wave("15991503272hzthzt")