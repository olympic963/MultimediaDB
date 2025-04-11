import librosa
import librosa.display
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt

# Đường dẫn file âm thanh
file_path = r'D:\Project\Multimedia Database\Dataset\Trombone\49478__n2p5__fanfarejazz1.flac'

# Đọc file âm thanh, không ép về mono
y, sr = librosa.load(file_path, sr=None, mono=False)

# Sử dụng soundfile để lấy metadata
with sf.SoundFile(file_path) as audio_file:
    num_channels = audio_file.channels
    metadata = {
        "Sample Rate": audio_file.samplerate,
        "Channels": num_channels,
        "Frames (Samples)": audio_file.frames,
        "Duration (seconds)": audio_file.frames / audio_file.samplerate,
        "Format": audio_file.format,
        "Subtype": audio_file.subtype
    }

# In metadata
print("=== Metadata của file âm thanh ===")
for key, value in metadata.items():
    print(f"{key}: {value}")

# Đảm bảo y có đúng số chiều cho stereo
if num_channels > 1:
    y = np.array(y)

# Vẽ waveform cho từng kênh
plt.figure(figsize=(12, 4 * num_channels))
for i in range(num_channels):
    plt.subplot(num_channels + 1, 1, i + 1)
    plt.plot(y[i], color='b', alpha=0.6)
    plt.title(f"Waveform - Channel {i+1}")
    plt.xlabel("Samples")
    plt.ylabel("Amplitude")

# Vẽ spectrogram (chỉ hiển thị tổng hợp nếu nhiều kênh)
plt.subplot(num_channels + 1, 1, num_channels + 1)
D = librosa.amplitude_to_db(np.abs(librosa.stft(y[0] if num_channels > 1 else y)), ref=np.max)
librosa.display.specshow(D, sr=sr, x_axis="time", y_axis="log", cmap="coolwarm")
plt.colorbar(format="%+2.0f dB")
plt.title("Spectrogram")

plt.tight_layout()
plt.show()
