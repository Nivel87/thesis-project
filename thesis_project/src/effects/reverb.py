import numpy as np
from scipy.signal import fftconvolve
from thesis_project.src.effects.audio_effect import AudioEffect


class ReverbEffect(AudioEffect):
    def __init__(self, t60: float, num_reflections: int, decay_rate: float):
        self.t60 = t60
        self.num_reflections = num_reflections
        self.decay_rate = decay_rate

    def create_reverb_ir(self, samplerate: int) -> np.ndarray:
        """
        Genera una risposta all'impulso (IR) sintetica per il riverbero.
        """
        ir_length = int(self.t60 * samplerate)
        ir = np.zeros(ir_length)

        ir[0] = 1.0

        for _ in range(self.num_reflections):
            delay = np.random.randint(1, ir_length)
            attenuation = np.exp(-delay / (samplerate * self.t60) * self.decay_rate)
            ir[delay] += attenuation * (np.random.rand() * 2 - 1)

        if np.max(np.abs(ir)) > 0:
            ir /= np.max(np.abs(ir))

        return ir

    def apply_effect(self, audio_signal: np.ndarray, samplerate: int) -> np.ndarray:
        """
        Applica l'effetto di riverbero tramite convoluzione.
        """
        ir = self.create_reverb_ir(samplerate)
        convolved_audio = fftconvolve(audio_signal, ir, mode='full')

        if np.max(np.abs(convolved_audio)) > 0:
            convolved_audio /= np.max(np.abs(convolved_audio))

        return convolved_audio