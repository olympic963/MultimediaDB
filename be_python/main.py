import librosa
import numpy as np
import os
import pygame
pygame.mixer.init()

folder_path = r'D:\Project\Multimedia Database\Dataset\Trombone'
for file in os.listdir(folder_path):
    print(file)

# file_path = os.path.join(folder_path, '172949__notr__sadtrombones.mp3')
file_path = r'D:\Project\Multimedia Database\Dataset\Trombone\49478__n2p5__fanfarejazz1.flac'
pygame.mixer.music.load(file_path)

# Play the audio file
pygame.mixer.music.play()

# Keep the program running until the audio is finished
while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)

# def feature_extraction(file_path):
#     # Load the audio file
#     x, sample_rate = librosa.load(file_path, res_type="kaiser_fast")
#     print(x)
#     print(sample_rate)
#     # Extract the MFCCs
#     mfccs = librosa.feature.mfcc(y=x, sr=sample_rate, n_mfcc=13)
#     print(mfccs)
#     # Calculate the mean of each coefficient across all frames
#     mfccs = np.mean(mfccs.T, axis=0)
#     print(mfccs)
#     return mfccs
#
# features = {}
# for file in os.listdir(folder_path):
#     file_path = os.path.join(folder_path, file)
#     print(file_path)
#     features[file] = feature_extraction(file_path)