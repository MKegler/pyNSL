"""
Demo usage of the pyNSL package.

Mikolaj Kegler, January 2021
"""
import matplotlib.pyplot as plt
import soundfile as sf
import pyNSL

# Load sample audio (for plotting)
audio, fs = sf.read('./SampleData/SX95.WAV')

# Set up parameters
paras = [8, 8, -2, -1]
# Window size: 8 ms
# Integration window: 8 ms
# Compression: -2 (linear, i.e. no compression)
# Octave shift: -1 (shift by 1 octave 16 kHz -> 8 kHz -> channel freqs. < 4 kHz)
srate_out = fs  # Output sampling rate

channels = pyNSL.wav2aud(audio, fs, paras, srate_out)

# Get center frequencies of cochlear filterbank for plotting
filterbank = pyNSL.pyNSL.get_filterbank()
# Use 8 kHz version, because octave shift was applied (paras[-1] = -1)
CFs = filterbank['CF_8kHz'].squeeze()

# Plotting
f, ax = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
ax[0].set_title('Audio')
ax[0].plot(audio)
ax[0].set_ylabel('Amplitude (a.u.)')
ax[1].set_title('Auditory Spectrogram')
ax[1].imshow(channels.T, aspect='auto', origin='lower')
ax[1].set_ylabel('Channel CFs (Hz)')
ax[1].set_xlabel('Samples (fs={} Hz)'.format(fs))

ticks = ax[1].get_yticks()
ticks = [int(t) for t in ticks[(ticks > -1) * (ticks < channels.shape[1])]]
ax[1].set_yticks(ticks)
ax[1].set_yticklabels(CFs[ticks].astype(int))

f.tight_layout()
f.savefig('Demo.pdf')

plt.show()
