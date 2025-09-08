import numpy as np
from thesis_project.src.effects.audio_effect import AudioEffect


class DelayEffect(AudioEffect):
    def __init__(self, delay_time: float, feedback: float, mix: float):
        """
        Inizializza l'effetto di delay.

        Args:
            delay_time (float): Tempo di ritardo in secondi.
            feedback (float): Percentuale del segnale ritardato da riaggiungere all'input per le ripetizioni successive. Valore tra 0.0 e 1.0.
            mix (float): Miscela tra il segnale originale e quello processato. Valore tra 0.0 e 1.0.
        """
        self.delay_time = delay_time
        self.feedback = feedback
        self.mix = mix

    def apply_effect(self, audio_signal: np.ndarray, samplerate: int) -> np.ndarray:
        """
        Applica l'effetto di delay al segnale audio.

        Args:
        - audio_signal (np.ndarray): Il segnale audio di input.
        - delay_time (float): Tempo di ritardo in secondi.
        - feedback (float): Percentuale del segnale ritardato da riaggiungere all'input per le ripetizioni successive.
        - mix (float): Miscela tra il segnale originale e quello processato.
        - samplerate (int): La frequenza di campionamento.

        Returns:
        - np.ndarray: Il segnale audio con l'effetto di delay applicato.
        """
        # Calcola il numero di campioni per il ritardo
        delay_samples = int(self.delay_time * samplerate)

        # Inizializza l'array di output con la stessa dimensione dell'input
        output_signal = np.zeros_like(audio_signal)

        # Calcola il segnale di ritardo (delay line)
        delayed_signal = np.zeros(audio_signal.shape, dtype=audio_signal.dtype)

        # Ciclo per creare le ripetizioni
        for i in range(len(audio_signal)):
            # Calcola l'indice di ritardo
            delay_index = i - delay_samples

            # Se l'indice di ritardo è valido (non negativo),
            # aggiunge il segnale ritardato all'output
            if delay_index >= 0:
                delayed_signal[i] = audio_signal[delay_index] + self.feedback * delayed_signal[delay_index]
            else:
                delayed_signal[i] = audio_signal[i]

        # Miscela il segnale originale con quello ritardato
        # mix = 0.5 significa 50% segnale originale e 50% segnale ritardato
        processed_signal = (1 - self.mix) * audio_signal + self.mix * delayed_signal

        # Normalizza l'output per evitare il clipping
        max_val = np.max(np.abs(processed_signal))
        if max_val > 0:
            processed_signal /= max_val

        return processed_signal