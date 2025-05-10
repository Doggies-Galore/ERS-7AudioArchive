import os
import numpy as np
from scipy.io import wavfile

def is_60hz_tone(segment, sample_rate, freq_target=60, tolerance=5, dominance_ratio=0.13):
    windowed = segment * np.hanning(len(segment))
    fft = np.fft.rfft(windowed)
    freqs = np.fft.rfftfreq(len(segment), 1 / sample_rate)
    magnitude = np.abs(fft)
    total_energy = np.sum(magnitude)
    band = (freqs >= (freq_target - tolerance)) & (freqs <= (freq_target + tolerance))
    band_energy = np.sum(magnitude[band])
    return (total_energy > 0) and (band_energy / total_energy > dominance_ratio)

def has_significant_audio(segment, threshold=500):
    """Checks if a segment contains significant audio based on RMS."""
    rms = np.sqrt(np.mean(segment.astype(float)**2))
    return rms > threshold

def split_on_tone(filename, tone_duration=0.5, tone_freq=60, threshold=0.02, min_segment_duration=0.5):
    sample_rate, audio = wavfile.read(filename)
    assert sample_rate == 96000, "Expected 96kHz sample rate"
    assert len(audio.shape) == 1, "Expected mono audio"

    tone_length_samples = int(tone_duration * sample_rate)
    step = int(sample_rate * 0.1)  # check every 0.1s
    min_segment_samples = int(min_segment_duration * sample_rate)

    markers = []
    for i in range(0, len(audio) - tone_length_samples, step):
        segment = audio[i:i + tone_length_samples]
        if is_60hz_tone(segment, sample_rate, threshold):
            markers.append(i)

    # Deduplicate nearby markers
    deduped = []
    for m in markers:
        if not deduped or m - deduped[-1] > tone_length_samples:
            deduped.append(m)

    # Split between tone midpoints
    parts = []
    prev = 0
    for idx in deduped:
        mid = idx + tone_length_samples // 2
        parts.append((prev, mid))
        prev = mid
    parts.append((prev, len(audio)))  # last part

    # Load action names
    with open("Actions.txt", "r", encoding="utf-8") as f:
        action_names = [line.strip() for line in f if line.strip()]

    # Ensure enough action names
    if len(action_names) < len(parts):
        raise ValueError("Not enough action names in the Actions.txt file!")

    # Output folder
    out_folder = "./SegmentedAudio"
    os.makedirs(out_folder, exist_ok=True)

    # Save segments with action-based filenames
    for i, (start, end) in enumerate(parts):
        # Adjust start and end to prevent overlap
        if i > 0:
            prev_end = parts[i - 1][1]
            if start < prev_end:
                start = prev_end
        if i < len(parts) - 1:
            next_start = parts[i + 1][0]
            if end > next_start:
                end = next_start

        segment = audio[start:end]
        action = action_names[i].replace(" ", "_")
        filename = f"{action}.wav"
        out_path = os.path.join(out_folder, filename)
        wavfile.write(out_path, sample_rate, segment.astype(np.int16))
        print(f"Saved: {out_path}")

if __name__ == "__main__":
    split_on_tone("ERS-7.wav", tone_duration=0.5, threshold=0.03)
