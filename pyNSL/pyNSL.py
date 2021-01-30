'''
Direct port of methods from NSL package.
Methods included in the module were all tested
against original MATLAB implementation.
---
Work in progress - use with caution!
'''

import numpy as np
import scipy.io as sio
from scipy import signal
import pkg_resources


def sigmoid(y, fac):
    """Cochlear (non)linearity. Monotonic increasing function which simulate hair cell nonlinearity.
    Args:
        y (1D array): input signal.
        fac ([type]): non-linear factor
            fac > 0, transister-like function
            fac = 0, hard-limiter (1/0)
            fac = -1, half-wave rectifier
            else, no operation, i.e., linear.
    Returns:
        y : transformed input signal.
    """
    if fac > 0:
        y = np.exp(-y/fac)
        y = 1./(1+y)
    elif fac == 0:
        y = (y > 0).astype(float)  # hard-limiter
    elif fac == -1:
        y[y < 0] = 0  # half-wave rectifier

    return y


def get_filterbank():
    """Getter returning Gammatone filter bank.
    Returns:
        filtbank [dict] : Filterbank + misc. info (CFs, etc.)
    """
    data_path = pkg_resources.resource_filename('pyNSL', 'aud24.mat')
    filtbank = sio.loadmat(data_path)
    return filtbank


def wav2aud(x, srate, paras=[8, 8, -2, -1], srate_out=None, COCHBA=None, verbose=False):
    """ WAV2AUD fast auditory spectrogram (Freqs: 180 - 7246 Hz)
    Since max frequencies ~4 kHz, x should be 16 kHz (srate)
    If it is not, the signal will be resampled to 16k.

    Args:
        x (1D array): Acoustic input signal.
        srate (float): Sampling rate of the audio signal in Hz.
        paras (list, optional): [frmlen, tc, fac, shft]. Defaults to [8,8,-2,-1].
            See the description below:
            frmlen: frame length, typically, 8, 16 or 2^[natural #] ms.
            tc: time const., typically, 4, 16, or 64 ms, etc. If tc == 0,
                the leaky integration turns to short-term avg.
            fac: nonlinear factor (critical level ratio), typically, .1 for
                a unit sequence, e.g., X -- N(0, 1); The less the value, the more the compression.
                - fac = 0,  y = (x > 0),      full compression, booleaner.
                - fac = -1, y = max(x, 0),    half-wave rectifier
                - fac = -2, y = x,            linear function
            shft : shifted by # of octave, e.g., 0 for 16k, -1 for 8k,
                etc. SF = 16K * 2^[shft].%
        srate_out ([int | float], optional): Sampling rate of the output.
            If None, the output will be frames of size params[0]. Defaults to None.
        COCHBA ([nd array], optional): Pre-loaded gammatone filter bank.
            If None, NSL filterbank will be loaded and used. Defaults to None.
        verbose (boolean, optional): Verbosity. Defaults to False.

    Returns:
        v5 [nd array]: the auditory spectrogram. Size: N-by-(M-1), where:
            N - number of frames (if srate_out=None), otherwise srate_out.
            M - number of filters in the filterbank (default: 129)
    """
    assert len(paras) == 4

    # Check the input sampling rate and (if necessary) resample
    if srate != 16000:
        if verbose:
            print('Resampling audio signal to 16 kHz')
        x = signal.resample_poly(x, 16000, srate)

    # If octave shift, decimate the signal
    if paras[-1] != 0:
        if verbose:
            print('Shifting by {} octave'.format(paras[-1]))
        x = signal.resample_poly(x, 1, 1 - paras[-1])

    # Load cochlear filterbank, if not pre-loaded
    if COCHBA is None:
        f = get_filterbank()
        COCHBA = f['COCHBA']
        del f

    (L, M) = COCHBA.shape  # p_max = L - 2
    L_x = len(x)  # length of input

    # octave shift, nonlinear factor, frame length, leaky integration
    shft = paras[3]  # octave shift (default -1, so 16kHz input -> 8 kHz)
    fac = paras[2]  # nonlinear factor (default -2 == linear)
    # frame length (points), paras[0] 8 -> miliseconds
    L_frm = np.round(paras[0] * 2**(4+shft)).astype(int)

    if paras[1]:
        alph = np.exp(-1/(paras[1]*2**(4+shft)))  # decaying factor
    else:
        alph = 0  # short-term avg.

    # hair cell time constant in ms
    haircell_tc = 0.5
    beta = np.exp(-1/(haircell_tc*2**(4+shft)))

    # get data, allocate memory for ouput
    N = np.ceil(L_x / L_frm).astype(int)  # No. of frames
    x_tmp = np.zeros(N * L_frm)
    x_tmp[0:len(x)] = x[:]
    x = x_tmp[:]
    del x_tmp
    v5 = np.zeros((N, M-1))

    # Processing last channel (highest frequency)
    p = COCHBA[0, M-1].real
    idx = np.arange(0, p+1, dtype=int) + 1
    B = COCHBA[idx, M-1].real
    A = COCHBA[idx, M-1].imag
    y1 = signal.lfilter(B, A, x)
    y2 = sigmoid(y1, fac)

    # Hair cell membrane (low-pass <= 4 kHz)
    # ignored for LINEAR ionic channels (fac == -2)
    if (fac != -2):
        y2 = signal.lfilter([1.], [1 - beta], y2)

    y2_h = y2[:]
    y3_h = 0

    for ch in (np.arange(M-1, 0, -1) - 1):
        p = COCHBA[0, ch].real
        idx = np.arange(0, p+1, dtype=int) + 1
        B = COCHBA[idx, ch].real
        A = COCHBA[idx, ch].imag
        y1 = signal.lfilter(B, A, x)

        # Ionic channels (sigmoid function)
        y2 = sigmoid(y1, fac)[:]

        # Hair cell membrane
        # (low-pass <= 4 kHz) ---> y2 (ignored for linear)
        if fac != -2:
            y2 = signal.lfilter([1.], [1 - beta], y2)

        # Lateral inhibitory network
        # masked by higher (frequency) spatial response
        y3 = y2[:] - y2_h[:]
        y2_h = y2[:]

        # half-wave rectifier ---> y4
        y4 = np.maximum(y3, np.zeros(len(y3)))

        # % temporal integration window ---> y5
        if alph:  # leaky integration
            y5 = signal.lfilter([1.], [1, -alph], y4)
            v5[:, ch] = y5[(L_frm*np.arange(1, N+1)) - 1]
        else:  # % short-term average
            if L_frm == 1:
                v5[:, ch] = y4
            else:
                v5[:, ch] = np.mean(y4.reshape(L_frm, N, order='F').copy())

    if srate_out:
        l = v5.shape[0]  # Lenght of the auditory spectrogram
        dt_idx = 1000/srate_out
        dt_idx = dt_idx/paras[0]
        idx_up = np.ceil(np.arange(dt_idx, l+0.1*dt_idx,
                                   dt_idx)).astype(np.int) - 1
        return v5[idx_up, :]
    else:
        return v5
