import numpy as np

def beep(frequency, duration, sample_rate=44100):
    """Generate a sine wave.

    Args:
        frequency: Float or int, represents frequency of sine wave.
        duration: Float or int, duration of the wave in seconds.
        sample_rate: Float or int, sampling rate for the wave.

    Returns:
        A 1-dimensional numpy array.
    """
    return np.sin(2 * np.pi * frequency * (np.arange(0, duration * sample_rate))/sample_rate)

def ramp_beep(frequency, duration, sample_rate=44100, proportion=0.1):
    """Generate a sine wave with a linear ramp.

    Args:
        frequency: Float or int, passed to `beep`.
        duration: Float or int, passed to `beep`.
        sample_rate: Float or int, passed to `beep`.
        proportion: Float on interval [0, 0.5], determines the duration of the ramping phase.

    Returns:
        A 1-dimensional numpy array.
    """
    out = beep(frequency, duration, sample_rate)
    ramp = np.linspace(0, 1, int(proportion * len(out)))
    out[:len(ramp)] *= ramp
    out[-len(ramp):] *= ramp[::-1]
    return out

def beep_train(click_freq=[440, 660, 880, 1220],
               inter_click_interval=0.5,
               num_clicks=4,
               dur_clicks=0.04,
               sample_rate=44100):
    """Generate a series of sine waves.

    Args:
        click_freq: List or tuple or 1d numpy array, used to specify the frequency of each beep.
        inter_click_interval: Float or int, the period between the beep midpoints.
        num_clicks: Int, number of clicks.
        dur_clicks: Float or int, duration of each click in seconds.
        sample_rate: Float or int, passed to `beep`.

    Returns:
        A 1-dimensional numpy array.
    """
    if len(click_freq) != 1 and len(click_freq) != num_clicks:
        raise ValueError('click_freq must be either 1 or match the num_clicks.')
    if len(click_freq) == 1:
        click_freq = [click_freq] * num_clicks
    beeps = [ramp_beep(n, duration=dur_clicks, sample_rate=sample_rate) for n in click_freq]
    space = np.zeros(int((inter_click_interval * sample_rate) - len(beeps[0])))
    out = np.zeros((int(sample_rate * 0.5 - len(beeps[0])/2)))
    out = np.append(out, beeps[0])
    for i in range(num_clicks - 1):
        out = np.append(out, space)
        out = np.append(out, beeps[i + 1])
    return out

if __name__ == '__main__':
    from psychopy import sound
    # hamming leads to audio defect
    # stereo is ignored for array (always stereo?)
    # reduce blockSize for lower latency(?)
    click_train = sound.Sound(beep_train(), blockSize=32, hamming=False)
    click_train.play()
