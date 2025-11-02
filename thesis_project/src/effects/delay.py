import numpy as np
from scipy.signal import fftconvolve  # Import necessario per la convoluzione
from thesis_project.src.effects.audio_effect import AudioEffect


class DelayEffect(AudioEffect):
    def __init__(self, delay_time: float, feedback: float, mix: float):
        """
            Inizializza l'effetto di delay.
        """
        self.delay_time = delay_time
        self.feedback = feedback
        self.mix = mix
        # Inizializza l'IR, che verrà calcolata al primo apply_effect o in una chiamata esplicita.
        self.mono_ir = None

    def create_delay_ir(self, samplerate: int, duration_seconds: float = 3.0) -> np.ndarray:
        """
            Crea la Risposta Impulsiva (IR) per il Delay Mono.

            Parametri in input:
            - samplerate: La frequenza di campionamento.
            - duration_seconds: Durata in secondi della IR per catturare tutte le code di feedback.

            Parametri in output:
            - final_ir: la risposta impulsiva del delay sottoforma di array numpy
        """
        delay_samples = int(self.delay_time * samplerate)

        # Assicura che la durata sia sufficiente per un delay
        if delay_samples == 0:
            return np.array([1.0], dtype=np.float32)

        # La durata dell'IR deve essere sufficiente per catturare il decay del feedback
        ir_length = int(duration_seconds * samplerate)

        # --- Generazione della coda WET (taps) ---
        ir_wet = np.zeros(ir_length, dtype=np.float32)

        # Impulso iniziale del segnale ritardato (primo tap)
        if delay_samples < ir_length:
            ir_wet[delay_samples] = 1.0

            # Loop ricorsivo per generare la coda di feedback
        # L'ampiezza di un tap è il tap precedente (ritardato) attenuato dal feedback
        for i in range(delay_samples * 2, ir_length):
            # i - delay_samples è la posizione del tap precedente
            # Solo la porzione ritardata (wet) alimenta il feedback
            ir_wet[i] = ir_wet[i - delay_samples] * self.feedback

        # --- Generazione del segnale DRY (impulso a t=0) ---
        ir_dry = np.zeros(ir_length, dtype=np.float32)
        ir_dry[0] = 1.0

        # --- Combinazione Dry/Wet per l'IR finale ---
        # final_ir = (1 - mix) * DRY + (mix) * WET
        final_ir = (1 - self.mix) * ir_dry + self.mix * ir_wet

        # Normalizzazione: Assicura che l'IR non causi clipping
        # (dovrebbe essere circa 1.0 se mix=1 e feedback < 1)
        max_val = np.max(np.abs(final_ir))
        if max_val > 0:
            final_ir /= max_val

        return final_ir

    def apply_effect(self, audio_signal: np.ndarray, samplerate: int, channel_mode: str = 'both') -> np.ndarray:
        """
            Applica l'effetto di delay al segnale audio tramite convoluzione.

            Parametri in input:
            - audio_signal: L'audio del segnale in ingresso
            - samplerate: La frequenza di campionamento
            -  channel_mode: Specifica quali canali devono essere elaborati ('both', 'right', 'left')
        """
        if self.mono_ir is None or samplerate != len(self.mono_ir) // 3:
            self.mono_ir = self.create_delay_ir(samplerate)

        mono_ir = self.mono_ir

        if audio_signal.ndim == 1:
            processed_signal = fftconvolve(audio_signal, mono_ir, mode='full')[:len(audio_signal)]

        elif audio_signal.ndim == 2:
            processed_signal = audio_signal.copy()

            # Nota: La lunghezza del segnale convoluto sarà len(audio_signal) + len(mono_ir) - 1.
            # Tronchiamo per mantenere la lunghezza originale.
            L_sig = len(audio_signal)

            if channel_mode == 'both':
                processed_signal[:, 0] = fftconvolve(audio_signal[:, 0], mono_ir, mode='full')[:L_sig]
                processed_signal[:, 1] = fftconvolve(audio_signal[:, 1], mono_ir, mode='full')[:L_sig]
            elif channel_mode == 'left':
                processed_signal[:, 0] = fftconvolve(audio_signal[:, 0], mono_ir, mode='full')[:L_sig]
            elif channel_mode == 'right':
                processed_signal[:, 1] = fftconvolve(audio_signal[:, 1], mono_ir, mode='full')[:L_sig]
            else:
                raise ValueError("Modalità canale non valida. Scegli tra 'both', 'left', o 'right'.")

        else:
            raise ValueError("Formato audio non supportato.")

        # Converto al tipo di dato originale (float32, etc.)
        processed_signal = processed_signal.astype(audio_signal.dtype)

        # Se il segnale risulta in clipping, aumenta duration_seconds nella IR o riduci il mix/feedback.

        return processed_signal



class PingPongDelayEffect(AudioEffect):
    def __init__(self, delay_time_l: float, delay_time_r: float, feedback: float, mix: float):
        """
            Inizializza l'effetto di Ping Pong Delay Asimmetrico.
        """
        self.delay_time_l = delay_time_l
        self.delay_time_r = delay_time_r
        self.feedback = feedback
        self.mix = mix
        self.stereo_ir = None

    def create_pingpong_ir(self, samplerate: int, duration_seconds: float = 3.0) -> np.ndarray:
        """
            Crea la Risposta Impulsiva Stereo (IR) per il Ping Pong Delay Asimmetrico.

            Parametri in input:
            - samplerate: La frequenza di campionamento.
            - duration_seconds: Durata in secondi della IR per catturare tutte le code di feedback.

            Parametri in output:
            - final_ir: La IR stereo (num_samples x 2).
        """
        delay_samples_l = int(self.delay_time_l * samplerate)
        delay_samples_r = int(self.delay_time_r * samplerate)
        max_delay_samples = max(delay_samples_l, delay_samples_r)

        ir_length = int(duration_seconds * samplerate)

        # Inizializza i buffer di delay (wet signal)
        ir_wet_l = np.zeros(ir_length, dtype=np.float32)
        ir_wet_r = np.zeros(ir_length, dtype=np.float32)

        # Inizializza l'impulso di input (Dry)
        ir_dry_l = np.zeros(ir_length, dtype=np.float32)
        ir_dry_r = np.zeros(ir_length, dtype=np.float32)

        ir_dry_l[0] = 1.0  # Inietto il segnale solo sul canale L
        # ir_dry_r[0] = 1.0

        current_signal_l = ir_dry_l.copy()
        current_signal_r = ir_dry_r.copy()

        for i in range(max_delay_samples, ir_length):
            # Calcolo Ritardo L (input secco L + feedback da R)
            feedback_from_r = self.feedback * ir_wet_r[i - delay_samples_r] if i >= delay_samples_r else 0.0

            # L'input *secco* ritardato da L passa nel buffer L (non c'è self.feedback su questo)
            delay_in_l = current_signal_l[i - delay_samples_l] + feedback_from_r
            ir_wet_l[i] = delay_in_l

            # Calcolo Ritardo R (input secco R + feedback da L)
            feedback_from_l = self.feedback * ir_wet_l[i - delay_samples_l] if i >= delay_samples_l else 0.0

            # L'input *secco* ritardato da R passa nel buffer R
            delay_in_r = current_signal_r[i - delay_samples_r] + feedback_from_l
            ir_wet_r[i] = delay_in_r

        final_ir_l = (1 - self.mix) * ir_dry_l + self.mix * ir_wet_l
        final_ir_r = (1 - self.mix) * ir_dry_r + self.mix * ir_wet_r

        final_ir = np.stack((final_ir_l, final_ir_r), axis=1)

        # Normalizzazione
        max_val = np.max(np.abs(final_ir))
        if max_val > 0:
            final_ir /= max_val

        return final_ir

    def apply_effect(self, audio_signal: np.ndarray, samplerate: int, channel_mode: str = 'both') -> np.ndarray:
        """
            Applica l'effetto di Ping Pong Delay Asimmetrico tramite convoluzione.
        """
        if audio_signal.ndim != 2:
            raise ValueError("Il Ping Pong Delay richiede un segnale stereo (ndim=2) per funzionare.")

        if self.stereo_ir is None or samplerate != len(self.stereo_ir) // 3:  # Ricalcola se necessario
            # Calcola l'IR necessaria per la convoluzione
            self.stereo_ir = self.create_pingpong_ir(samplerate)

        stereo_ir = self.stereo_ir
        num_samples = audio_signal.shape[0]

        # La convoluzione stereo è l'IR Left con il segnale Left, e l'IR Right con il segnale Right
        processed_signal_l = fftconvolve(audio_signal[:, 0], stereo_ir[:, 0], mode='full')[:num_samples]
        processed_signal_r = fftconvolve(audio_signal[:, 1], stereo_ir[:, 1], mode='full')[:num_samples]

        processed_signal = np.stack((processed_signal_l, processed_signal_r), axis=1)

        # Normalizzazione
        max_val = np.max(np.abs(processed_signal))
        if max_val > 0:
            processed_signal = (processed_signal / max_val).astype(audio_signal.dtype)

        return processed_signal