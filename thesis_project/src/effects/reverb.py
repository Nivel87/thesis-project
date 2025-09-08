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

        Parametri:
        - t60 (float): Il tempo di decadimento del riverbero in secondi.
        - samplerate (int): La frequenza di campionamento del segnale audio.
        - num_reflections (int): Numero di riflessioni (impulsi) da generare.
        - decay_rate (float): Tasso di decadimento esponenziale delle riflessioni.

        Ritorna:
        - ir (np.ndarray): L'array numpy che rappresenta l'IR.
        """
        ir_length = int(self.t60 * samplerate)
        ir = np.zeros(ir_length)

        #Primo impulso a tempo zero
        ir[0] = 1.0

        #Genera riflessioni casuali (impulsi), con posizioni e ampiezze casuali
        for _ in range(self.num_reflections):
            delay = np.random.randint(1, ir_length)
            # Calcola l'attenuazione esponenziale
            attenuation = np.exp(-delay / (samplerate * self.t60) * self.decay_rate)
            # Aggiunge l'impulso all'IR con una certa casualità
            ir[delay] += attenuation * (np.random.rand() * 2 - 1)

        # Normalizza l'IR per evitare saturazione (clipping)
        if np.max(np.abs(ir)) > 0:
            ir /= np.max(np.abs(ir))

        return ir

    def apply_effect(self, audio_signal: np.ndarray, samplerate: int) -> np.ndarray:
        """
        Applica l'effetto di riverbero tramite convoluzione.

        Parametri:
        - audio_signal (np.ndarray): Il segnale audio da processare.
        - ir (np.ndarray): La risposta all'impulso (IR) del riverbero.

        Ritorna:
        - convolved_audio (np.ndarray): Il segnale audio con il riverbero applicato.
        """
        ir = self.create_reverb_ir(samplerate)
        # Esegue la convoluzione con FFT nel dominio della frequenza
        convolved_audio = fftconvolve(audio_signal, ir, mode='full')

        #normalizza il segnale audio di output
        if np.max(np.abs(convolved_audio)) > 0:
            convolved_audio /= np.max(np.abs(convolved_audio))

        return convolved_audio