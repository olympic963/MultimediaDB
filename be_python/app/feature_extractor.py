import os
import numpy as np
import librosa
import logging
from typing import Tuple, List, Dict, Union
import soundfile as sf

from app.config import SAMPLE_RATE, N_MFCC, HOP_LENGTH, N_FFT

logger = logging.getLogger(__name__)

class AudioFeatureExtractor:
    """
    Trích xuất đặc trưng từ file audio
    """

    def __init__(self):
        self.sr = SAMPLE_RATE
        self.n_mfcc = N_MFCC
        self.hop_length = HOP_LENGTH
        self.n_fft = N_FFT

    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        Đọc file audio từ đường dẫn

        Args:
            file_path: Đường dẫn đến file audio

        Returns:
            Tuple chứa dữ liệu audio và sample rate
        """
        try:
            y, sr = librosa.load(file_path, sr=self.sr, mono=False)  # Không ép mono để giữ số kênh
            return y, sr
        except Exception as e:
            logger.error(f"Không thể đọc file audio: {file_path}. Lỗi: {str(e)}")
            raise

    def extract_mfcc(self, y: np.ndarray, sr: int) -> np.ndarray:
        """
        Trích xuất MFCC (Mel-Frequency Cepstral Coefficients) từ audio signal

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            MFCC features
        """
        try:
            # Nếu là stereo, lấy kênh đầu tiên
            y_mono = y if y.ndim == 1 else y[0]
            mfccs = librosa.feature.mfcc(
                y=y_mono,
                sr=sr,
                n_mfcc=self.n_mfcc,
                hop_length=self.hop_length,
                n_fft=self.n_fft
            )
            mfccs_mean = np.mean(mfccs, axis=1)
            return mfccs_mean
        except Exception as e:
            logger.error(f"Không thể trích xuất MFCC. Lỗi: {str(e)}")
            raise

    def extract_spectral_contrast(self, y: np.ndarray, sr: int) -> np.ndarray:
        """
        Trích xuất spectral contrast từ audio signal

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            Spectral contrast features
        """
        y_mono = y if y.ndim == 1 else y[0]
        contrast = librosa.feature.spectral_contrast(y=y_mono, sr=sr, n_fft=self.n_fft, hop_length=self.hop_length)
        contrast_mean = np.mean(contrast, axis=1)
        return contrast_mean

    def extract_chroma(self, y: np.ndarray, sr: int) -> np.ndarray:
        """
        Trích xuất chroma từ audio signal

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            Chroma features
        """
        y_mono = y if y.ndim == 1 else y[0]
        chroma = librosa.feature.chroma_stft(y=y_mono, sr=sr, n_fft=self.n_fft, hop_length=self.hop_length)
        chroma_mean = np.mean(chroma, axis=1)
        return chroma_mean

    def extract_features(self, file_path: str) -> Dict:
        """
        Trích xuất đặc trưng và metadata từ file audio

        Args:
            file_path: Đường dẫn đến file audio

        Returns:
            Dictionary chứa vector đặc trưng và metadata
        """
        try:
            # Đọc file audio
            y, sr = self.load_audio(file_path)

            # Trích xuất các đặc trưng
            mfcc_features = self.extract_mfcc(y, sr)
            contrast_features = self.extract_spectral_contrast(y, sr)
            chroma_features = self.extract_chroma(y, sr)

            # Kết hợp các đặc trưng
            combined_features = np.concatenate([mfcc_features, contrast_features, chroma_features])

            # Chuẩn hóa vector đặc trưng
            feature_vector = combined_features / np.linalg.norm(combined_features)

            # Lấy metadata
            file_name = os.path.basename(file_path)
            file_type = os.path.splitext(file_path)[1].lower()
            file_size_kb = os.path.getsize(file_path) / 1024  # Kích thước file (KB)
            duration = librosa.get_duration(y=y, sr=sr)  # Thời lượng (giây)
            channel = 1 if y.ndim == 1 else y.shape[0]  # Số kênh (mono/stereo)
            samples = y.shape[-1]  # Tổng số mẫu
            sample_rate = sr  # Tần số lấy mẫu

            # Lấy subtype bằng soundfile
            with sf.SoundFile(file_path) as f:
                subtype = f.subtype

            return {
                "vector": feature_vector,
                "file_name": file_name,
                "file_type": file_type,
                "file_size_kb": file_size_kb,
                "sample_rate": int(sample_rate),
                "channel": int(channel),
                "samples": int(samples),
                "duration": float(duration),
                "subtype": subtype
            }
        except Exception as e:
            logger.error(f"Không thể trích xuất đặc trưng từ file {file_path}. Lỗi: {str(e)}")
            raise

    def process_audio_directory(self, directory_path: str) -> Dict[str, Dict]:
        """
        Xử lý tất cả các file audio trong thư mục và trích xuất đặc trưng cùng metadata

        Args:
            directory_path: Đường dẫn đến thư mục chứa file audio

        Returns:
            Dictionary với key là đường dẫn file, value là dict chứa vector và metadata
        """
        feature_dict = {}

        # Lặp qua tất cả các file trong thư mục
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.lower().endswith(('.wav', '.mp3', '.flac', '.ogg')):
                    file_path = os.path.join(root, file)
                    try:
                        # Trích xuất đặc trưng và metadata
                        features = self.extract_features(file_path)
                        feature_dict[file_path] = features
                        logger.info(f"Đã trích xuất đặc trưng từ: {file_path}")
                    except Exception as e:
                        logger.error(f"Lỗi khi xử lý file {file_path}: {str(e)}")
                        continue

        return feature_dict