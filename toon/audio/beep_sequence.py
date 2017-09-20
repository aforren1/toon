"""
.. module:: audio
     :platform: Unix, Windows
     :synopsis: Tools for generating auditory stimuli.

.. moduleauthor:: Alexander Forrence <aforren1@jhu.edu>

"""
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

    For example, to generate a sine wave with a frequency of 440 Hz,
    a duration of half a second, and a sampling rate of 44.1 kHz,
        >>> my_beep = beep(440, 0.5, 44100)
    """
    return np.sin(2 * np.pi * frequency * (np.arange(0, duration * sample_rate)) / sample_rate)


def ramp_beep(frequency, duration, sample_rate=44100, proportion=0.1):
    """Generate a sine wave with a linear ramp.

    Args:
        frequency (int or float): The frequency of the sine wave.
        duration (int or float): Duration of the beep in seconds.

    Kwargs:
        sample_rate (int or float): Sampling rate for the wave.
        proportion (float): On the interval [0, 0.5], determines the duration of the ramp phase.

    Returns:
        A 1-dimensional numpy array.

    For example, to generate a sine wave with a frequency of 440 Hz,
    a duration of half a second, a sampling rate of 44.1 kHz, and
    ramping up or down for the entirety of the beep,
        >>> my_beep = ramp_beep(440, 0.5, 44100, 0.5)
    """
    out = beep(frequency, duration, sample_rate)
    ramp = np.linspace(0, 1, int(proportion * len(out)))
    out[:len(ramp)] *= ramp
    out[-len(ramp):] *= ramp[::-1]
    return out


def beep_sequence(click_freq=[440, 660, 880, 1220],
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

    For example, to generate four beeps of different frequency and spaced by
    half a second,be
        >>> my_train = beep_sequence([1220, 400, 410, 620], inter_click_interval=0.5)
    """
    if len(click_freq) != 1 and len(click_freq) != num_clicks:
        raise ValueError('click_freq must be either 1 or match the num_clicks.')
    if len(click_freq) == 1:
        click_freq = [click_freq] * num_clicks
    beeps = [ramp_beep(n, duration=dur_clicks, sample_rate=sample_rate) for n in click_freq]
    space = np.zeros(int((inter_click_interval * sample_rate) - len(beeps[0])))
    out = np.zeros((int(sample_rate * 0.5 - len(beeps[0]) / 2)))
    out = np.append(out, beeps[0])
    for i in range(num_clicks - 1):
        out = np.append(out, space)
        out = np.append(out, beeps[i + 1])
    return out
