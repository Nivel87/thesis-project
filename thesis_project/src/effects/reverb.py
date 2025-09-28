import numpy as np
from scipy.signal import fftconvolve
from thesis_project.src.effects.audio_effect import AudioEffect


class ReverbEffect(AudioEffect):
    def __init__(self, t60: float, num_reflections: int, decay_rate: float, mix: float):
        """
            Inizializza l'effetto di riverbero.

            Parametri in input:
            - t60: Tempo di riduzione del livello di pressione sonora a -60 dB
            - num_reflections: densità delle prime riflessioni
            - decay_rate: decadimento exp
            - mix: Miscela dry/wet.
        """

        self.t60 = t60
        self.num_reflections = num_reflections
        self.decay_rate = decay_rate
        self.mix = np.clip(mix, 0.0, 1.0)


    def create_reverb_ir(self, samplerate: int) -> np.ndarray:
        """
            Genera una risposta all'impulso (IR) sintetica per il riverbero.

            Parametri in input:
            - samplerate: La frequenza di campionamento del segnale audio.

            Parametri in output:
            - ir: L'array Numpy che rappresenta l'IR.
        """

        ir_length = int(self.t60 * samplerate)
        ir = np.zeros(ir_length)

        ir[0] = 1.0

        #Genera riflessioni casuali (impulsi), con posizioni e ampiezze casuali
        for _ in range(self.num_reflections):
            delay = np.random.randint(1, ir_length)
            attenuation = np.exp(-delay / (samplerate * self.t60) * self.decay_rate)
            ir[delay] += attenuation * (np.random.rand() * 2 - 1)

        if np.max(np.abs(ir)) > 0:
            ir /= np.max(np.abs(ir))

        return ir


    def apply_effect(self, audio_signal: np.ndarray, samplerate: int, channel_mode: str = 'both') -> np.ndarray:
        """
            Applica l'effetto di riverbero tramite convoluzione.

            Parametri in input:
            - audio_signal: Il segnale audio da processare
            - samplerate: La frequenza di campionamento
            - channel_mode: Specifica quali canali devono essere elaborati ('both', 'right', 'left')

            Parametri in output:
            - processed_signal: Il segnale audio con il riverbero applicato.
        """
        ir = self.create_reverb_ir(samplerate)
        original_signal = audio_signal.copy()

        if audio_signal.ndim == 1:
            processed_signal = fftconvolve(audio_signal, ir, mode='full')[:len(audio_signal)]
            processed_signal = (1 - self.mix) * original_signal + self.mix * processed_signal

        elif audio_signal.ndim == 2:
            processed_signal = original_signal.copy()

            if channel_mode == 'both' or channel_mode == 'left':
                processed_signal[:, 0] = fftconvolve(audio_signal[:, 0], ir, mode='full')[:len(audio_signal)]

            if channel_mode == 'both' or channel_mode == 'right':
                processed_signal[:, 1] = fftconvolve(audio_signal[:, 1], ir, mode='full')[:len(audio_signal)]

        else:
            raise ValueError("Formato audio non supportato.")

        if np.max(np.abs(processed_signal)) > 0:
            processed_signal /= np.max(np.abs(processed_signal))

        return processed_signal