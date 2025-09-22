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


    def apply_effect(self, audio_signal: np.ndarray, samplerate: int, channel_mode: str = 'both') -> np.ndarray:
        """
            Applica l'effetto di delay al segnale audio.

            Parametri in input:
            - audio_signal: Il segnale audio originale
            - samplerate: La frequenza di campionamento
            - channel_mode: Specifica quali canali devono essere elaborati ('both', 'right', 'left')

            Parametri in output:
            - processed_signal: Il segnale audio con l'effetto di delay applicato.
        """
        if audio_signal.ndim == 1:
            processed_signal = self._process_mono(audio_signal, samplerate)

        elif audio_signal.ndim == 2:
            processed_signal = audio_signal.copy()

            if channel_mode == 'both':
                processed_signal[:, 0] = self._process_mono(audio_signal[:, 0], samplerate)
                processed_signal[:, 1] = self._process_mono(audio_signal[:, 1], samplerate)
            elif channel_mode == 'left':
                processed_signal[:, 0] = self._process_mono(audio_signal[:, 0], samplerate)
            elif channel_mode == 'right':
                processed_signal[:, 1] = self._process_mono(audio_signal[:, 1], samplerate)
            else:
                raise ValueError("Modalità canale non valida. Scegli tra 'both', 'left', o 'right'.")

        else:
            raise ValueError("Formato audio non supportato.")

        # Normalizzazione
        max_val = np.max(np.abs(processed_signal))
        if max_val > 0:
            processed_signal /= max_val

        return processed_signal

    def _process_mono(self, signal: np.ndarray, samplerate: int) -> np.ndarray:
        """ Metodo helper per la logica di elaborazione mono.

            Parametri in input:
            - signal: Il segnale audio originale
            - samplerate: La frequenza di campionamento

            Parametri in output:
            - processed_signal: Il segnale processato mono
        """
        delay_samples = int(self.delay_time * samplerate)
        num_samples = len(signal)
        delayed_signal = np.zeros(num_samples, dtype=signal.dtype)
        processed_signal = signal.copy()

        # Esegue il calcolo del delay e del feedback per il canale mono
        for i in range(delay_samples, num_samples):
            delayed_signal[i] = processed_signal[i - delay_samples] + self.feedback * delayed_signal[i - delay_samples]

        # Miscela dry/wet
        processed_signal = (1 - self.mix) * signal + self.mix * delayed_signal
        return processed_signal