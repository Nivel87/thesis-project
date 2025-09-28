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
        """ Metodo helper per la logica di elaborazione mono. """
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


class PingPongDelayEffect(AudioEffect):  # Non ereditiamo più da DelayEffect
    def __init__(self, delay_time_l: float, delay_time_r: float, feedback: float, mix: float):
        """
            Inizializza l'effetto di Ping Pong Delay Asimmetrico.

            Parametri in input:
            - delay_time_l: Tempo di ritardo in secondi per il canale Sinistro (L->R).
            - delay_time_r: Tempo di ritardo in secondi per il canale Destro (R->L).
            - feedback: Percentuale del segnale ritardato da riaggiungere.
            - mix: Miscela dry/wet.
        """
        self.delay_time_l = delay_time_l
        self.delay_time_r = delay_time_r
        self.feedback = feedback
        self.mix = mix

    def apply_effect(self, audio_signal: np.ndarray, samplerate: int, channel_mode: str = 'both') -> np.ndarray:
        """
            Applica l'effetto di Ping Pong Delay Asimmetrico.
            Questo effetto richiede **sempre** un segnale stereo (ndim=2).
        """
        if audio_signal.ndim != 2:
            raise ValueError("Il Ping Pong Delay richiede un segnale stereo (ndim=2) per funzionare.")

        num_samples = audio_signal.shape[0]

        # Calcola il ritardo in campioni per ogni direzione
        delay_samples_l = int(self.delay_time_l * samplerate)
        delay_samples_r = int(self.delay_time_r * samplerate)

        # Determina il buffer più grande necessario
        max_delay_samples = max(delay_samples_l, delay_samples_r)

        processed_signal = audio_signal.copy()

        # Inizializza i buffer di delay (wet signal)
        delay_buffer_l = np.zeros(num_samples, dtype=audio_signal.dtype)
        delay_buffer_r = np.zeros(num_samples, dtype=audio_signal.dtype)

        # Segnali di input (dry)
        signal_l = audio_signal[:, 0]
        signal_r = audio_signal[:, 1]

        # L'elaborazione inizia dopo il punto del ritardo più lungo
        for i in range(max_delay_samples, num_samples):

            # Calcolo del ritardo per il canale Sinistro (L)
            # Input Ritardato (Wet) L: Input secco di L MA il feedback (wet) arriva da R
            if i >= delay_samples_r:
                delay_in_l = signal_l[i - delay_samples_l] + self.feedback * delay_buffer_r[i - delay_samples_r]
            else:
                # Per i primi campioni (fino al ritardo L) il delay è solo il segnale secco ritardato
                delay_in_l = signal_l[i - delay_samples_l]

            delay_buffer_l[i] = delay_in_l

            # Calcolo del ritardo per il canale Destro (R)
            # Input Ritardato (Wet) R: Input secco di R MA il feedback (wet) arriva da L
            if i >= delay_samples_l:
                delay_in_r = signal_r[i - delay_samples_r] + self.feedback * delay_buffer_l[i - delay_samples_l]
            else:
                # Per i primi campioni (fino al ritardo R) il delay è solo il segnale secco ritardato
                delay_in_r = signal_r[i - delay_samples_r]

            delay_buffer_r[i] = delay_in_r

        # Miscela dry/wet per i canali
        processed_signal[:, 0] = (1 - self.mix) * signal_l + self.mix * delay_buffer_l
        processed_signal[:, 1] = (1 - self.mix) * signal_r + self.mix * delay_buffer_r

        # Normalizzazione
        max_val = np.max(np.abs(processed_signal))
        if max_val > 0:
            processed_signal /= max_val

        return processed_signal