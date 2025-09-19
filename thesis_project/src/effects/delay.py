import numpy as np
from thesis_project.src.effects.audio_effect import AudioEffect


class DelayEffect(AudioEffect):
    def __init__(self, delay_time: float, feedback: float, mix: float):
        """
            Inizializza l'effetto di delay.

            Parametri in input:
            - delay_time: Tempo di ritardo in secondi.
            - feedback: Percentuale del segnale ritardato da riaggiungere all'input per le ripetizioni successive. Valore tra 0.0 e 1.0.
            - mix: Miscela dry/wet. Valore tra 0.0 e 1.0.
        """
        self.delay_time = delay_time
        self.feedback = feedback
        self.mix = mix


    def apply_effect(self, audio_signal: np.ndarray, samplerate: int) -> np.ndarray:
        """
            Applica l'effetto di delay al segnale audio.

            Parametri in input:
            - audio_signal: Il segnale audio originale
            - samplerate: La frequenza di campionamento.

            Parametri in output:
            - processed_signal: Il segnale audio con l'effetto di delay applicato.
        """

        delay_samples = int(self.delay_time * samplerate)
        num_samples = len(audio_signal)

        delayed_signal = np.zeros(num_samples, dtype=audio_signal.dtype)

        processed_signal = audio_signal.copy()

        # Esegue il calcolo del delay e del feedback
        for i in range(delay_samples, num_samples):
            # Aggiunge il segnale originale ritardato...
            delayed_signal[i] = processed_signal[i - delay_samples]
            # ...più il segnale ritardato precedente per il feedback
            delayed_signal[i] += self.feedback * delayed_signal[i - delay_samples]

        # Miscela il segnale originale (dry) e quello ritardato (wet)
        processed_signal = (1 - self.mix) * audio_signal + self.mix * delayed_signal

        # Normalizzazione
        max_val = np.max(np.abs(processed_signal))
        if max_val > 0:
            processed_signal /= max_val

        return processed_signal