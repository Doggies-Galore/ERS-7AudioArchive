import os
import numpy as np
from scipy.io import wavfile

def is_60hz_tone(segment, sample_rate, freq_target=60, tolerance=5, dominance_ratio=0.1, min_band_energy=1e4):
    windowed = segment * np.hanning(len(segment))
    fft = np.fft.rfft(windowed)
    freqs = np.fft.rfftfreq(len(segment), 1 / sample_rate)

    magnitude = np.abs(fft)
    total_energy = np.sum(magnitude)
    band = (freqs >= (freq_target - tolerance)) & (freqs <= (freq_target + tolerance))
    band_energy = np.sum(magnitude[band])

    return (band_energy / (total_energy + 1e-10)) > dominance_ratio and band_energy > min_band_energy

def split_on_tone(filename, tone_duration=0.5, tone_freq=60, threshold=0.03, output_folder="./SegmentedAudio"):
    sample_rate, audio = wavfile.read(filename)
    assert sample_rate == 96000, "Expected 96kHz sample rate"
    assert len(audio.shape) == 1, "Expected mono audio"

    tone_length_samples = int(tone_duration * sample_rate)
    step = int(sample_rate * 0.1)

    markers = []
    for i in range(0, len(audio) - tone_length_samples, step):
        segment = audio[i:i + tone_length_samples]
        if is_60hz_tone(segment, sample_rate):
            markers.append(i)

    deduped = []
    for m in markers:
        if not deduped or m - deduped[-1] > tone_length_samples:
            deduped.append(m)

    parts = []
    prev = 0
    for idx in deduped:
        mid = idx + tone_length_samples // 2
        parts.append((prev, mid))
        prev = mid
    parts.append((prev, len(audio)))

    os.makedirs(output_folder, exist_ok=True)

    # Read action names
    action_file = "Actions.txt"
    if os.path.exists(action_file):
        with open(action_file, "r", encoding="utf-8") as f:
            action_names = [line.strip() for line in f if line.strip()]
    else:
        action_names = []

    for i, (start, end) in enumerate(parts):
        segment = audio[start:end]
        if i < len(action_names):
            name = action_names[i].replace(" ", "_")
        else:
            name = f"part_{i:02d}"
        out_path = os.path.join(output_folder, f"{name}.wav")
        wavfile.write(out_path, sample_rate, segment.astype(np.int16))
        print(f"Saved: {out_path}")

if __name__ == "__main__":
    split_on_tone("7Test.wav")
