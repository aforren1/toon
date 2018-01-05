import numpy as np


def beep(frequency, duration, sample_rate=44100):
    """Generates a sine wave.

    Args:
        frequency (int or float): The frequency of the sine wave.
        duration (int or float): Duration of the beep in seconds.

    Kwargs:
        sample_rate (int or float): Sampling rate for the wave.

    Returns:
        A 1-dimensional numpy array.

    Example:
        Generate a sine wave at 440 Hz and duration of 0.5 seconds:

        >>> my_beep = beep(440, 0.5, 44100)
    """
    sample = np.sin(2 * np.pi * frequency * (np.arange(0, int(duration * sample_rate))) / sample_rate)
    return sample

def decay_beep(frequency, duration, div=5, coef=0.01, sample_rate=44100):
    len_samples = int(duration * sample_rate)
    prop = len_samples // div
    beep = np.sin(2 * np.pi * frequency * (np.arange(0, len_samples)) / sample_rate)
    ramp_down = np.exp(-0.01 * np.arange(0, prop))
    ramp_up = np.flipud(ramp_down)
    beep[:prop] *= ramp_up
    beep[-prop:] *= ramp_down
    # apply hanning window
    hw_size = int(min(sample_rate // 200, len(beep) // 15))
    hw = np.hanning(2 * hw_size + 1)
    beep[:hw_size] *= hw[:hw_size]
    beep[-hw_size:] *= hw[hw_size + 1:]
    return beep

def beep_sequence(click_freq=(440, 660, 880, 1220),
                  inter_click_interval=0.5,
                  num_clicks=4,
                  dur_clicks=0.04,
                  sample_rate=44100):
    """Generate a series of linearly ramped sine waves.

    Kwargs:
        click_freq (list, tuple, or 1d numpy array): The frequency of each beep.
        inter_click_interval (int or float): The period between the beep midpoints.
        num_clicks (int): Number of clicks.
        dur_clicks (int or float): Float or int, duration of each beep in seconds.
        sample_rate (int or float): Sampling rate for the wave.

    Returns:
        A 1-dimensional numpy array.

    Notes:
        There's a 100 millisecond pause before the *center* of the first beep.

    Example:
        To generate four beeps of different frequency and spaced by half a second,

        >>> my_train = beep_sequence([1220, 400, 410, 620], inter_click_interval=0.5)
    """
    if len(click_freq) != 1 and len(click_freq) != num_clicks:
        raise ValueError('click_freq must be either 1 or match the num_clicks.')
    if len(click_freq) == 1:
        click_freq = click_freq * num_clicks
    beeps = [decay_beep(n, duration=dur_clicks, sample_rate=sample_rate) for n in click_freq]
    space = np.zeros(int((inter_click_interval * sample_rate) - len(beeps[0])))
    out = np.zeros((int(sample_rate * 0.1 - len(beeps[0]) / 2)))
    out = np.append(out, beeps[0])
    for i in range(num_clicks - 1):
        out = np.append(out, space)
        out = np.append(out, beeps[i + 1])
    return out
