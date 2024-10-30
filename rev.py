import numpy as np
import pyaudio
import wave
from scipy.fft import fft

# 参数配置
SAMPLE_RATE = 80000  # 与发送端保持一致
DURATION_PER_BIT = 0.1  # 每个比特的时长（秒）
FREQ0 = 500  # 表示“0”的频率
FREQ1 = 10000  # 表示“1”的频率


# 检测频率
def detect_frequency(chunk, sample_rate):
    spectrum = np.abs(fft(chunk))[:len(chunk) // 2]
    freqs = np.fft.fftfreq(len(spectrum), 1 / sample_rate)[:len(chunk) // 2]
    return freqs[np.argmax(spectrum)]


# 录音
def record_audio(sample_rate=SAMPLE_RATE):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, input=True, frames_per_buffer=1024)
    frames = []

    print("按回车键开始录音...")
    input()  # 等待用户按下回车键开始录音
    print("开始录音，按回车键停止录音")

    while True:
        data = stream.read(1024)
        frames.append(data)

        if input() == "":  # 再次按回车键停止录音
            print("录音结束")
            break

    stream.stop_stream()
    stream.close()
    p.terminate()

    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
    return audio_data, sample_rate


# 从 .wav 文件读取音频数据
def read_wav_file(file_path):
    with wave.open(file_path, 'rb') as wf:
        sample_rate = wf.getframerate()
        frames = wf.readframes(wf.getnframes())
        audio_data = np.frombuffer(frames, dtype=np.int16)
    return audio_data, sample_rate


# 解码音频信号
def decode_audio(audio_data, sample_rate, freq0=FREQ0, freq1=FREQ1, duration=DURATION_PER_BIT):
    chunk_size = int(sample_rate * duration)
    binary = ''

    for i in range(0, len(audio_data), chunk_size):
        chunk = audio_data[i:i + chunk_size]
        if len(chunk) == 0:
            continue

        dominant_freq = detect_frequency(chunk, sample_rate)

        # 根据频率判断0或1
        if abs(dominant_freq - freq0) < abs(dominant_freq - freq1):
            binary += '0'
        else:
            binary += '1'

    # 二进制数据转换为文本
    text = ""
    for i in range(0, len(binary), 8):
        byte = binary[i:i + 8]
        if len(byte) == 8:
            try:
                char = chr(int(byte, 2))
                if 32 <= ord(char) <= 126:
                    text += char
            except ValueError:
                continue

    return text


# 主程序
def main():
    choice = input("选择输入方式：1. 录音  2. 从文件读取 (输入1或2): ")

    if choice == "1":
        audio_data, sample_rate = record_audio()
    elif choice == "2":
        file_path = "./audio_signal.wav"  # 根目录的 .wav 文件路径
        audio_data, sample_rate = read_wav_file(file_path)
    else:
        print("无效选择")
        return

    decoded_text = decode_audio(audio_data, sample_rate)
    print("接收到的文本:", decoded_text)

    # 将解码后的文本保存到 wifi.txt 文件中
    with open("wifi.txt", "w", encoding="utf-8") as file:
        file.write(decoded_text)
    print("解码结果已保存到 wifi.txt")


if __name__ == "__main__":
    main()