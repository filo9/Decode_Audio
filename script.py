import numpy as np
import pyaudio
import wave
from threading import Thread

class AudioRecorder:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.frames = []
        self.is_recording = False
        self.stream = None
        self.p = pyaudio.PyAudio()

    def start_recording(self):
        """开始录音"""
        self.frames = []
        self.is_recording = True
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=self.sample_rate, input=True, frames_per_buffer=1024)

        # 启动线程录音
        self.recording_thread = Thread(target=self._record)
        self.recording_thread.start()
        print("开始录音...")

    def _record(self):
        """录音线程函数"""
        while self.is_recording:
            data = self.stream.read(1024)
            self.frames.append(data)

    def stop_recording(self):
        """停止录音并返回音频数据"""
        self.is_recording = False
        self.recording_thread.join()  # 等待录音线程结束
        self.stream.stop_stream()
        self.stream.close()
        print("录音结束")

        # 将录音数据转换为 numpy 数组
        audio_data = np.frombuffer(b''.join(self.frames), dtype=np.int16)
        return audio_data

    def save_to_file(self, filename="recorded_audio.wav"):
        """保存录音到文件"""
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.frames))
        print(f"录音文件已保存：{filename}")

    def close(self):
        """关闭资源"""
        self.p.terminate()

# 示例用法
recorder = AudioRecorder(sample_rate=44100)

# 手动控制录音的开始和结束
input("按 Enter 开始录音...")
recorder.start_recording()  # 开始录音

input("按 Enter 结束录音...")
audio_data = recorder.stop_recording()  # 停止录音

# 保存录音数据到文件
recorder.save_to_file("recorded_audio.wav")

# 清理资源
recorder.close()