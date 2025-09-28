import numpy as np
from scipy.signal import fftconvolve, resample_poly
import soundfile as sf
from thesis_project.src.effects.audio_effect import AudioEffect
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
IR_CABINET_PATH = BASE_DIR / "ir_cabinet"

class CabinetEffect(AudioEffect):
    def __init__(self, ir_name: str, mix: float = 1.0):
        """
        Inizializza l'effetto di simulazione Cabinet/Speaker.

        Parametri in input:
        - ir_path: Percorso del file audio (ad es. .wav) contenente la Risposta all'Impulso (IR) del cabinet.
        - mix: Miscela dry/wet. Valore tra 0.0 (solo segnale originale) e 1.0 (solo segnale processato).
        """
        self.ir_path = IR_CABINET_PATH / ir_name # COSTRUISCE IL PERCORSO COMPLETO
        self.mix = np.clip(mix, 0.0, 1.0)  # Assicura che mix sia tra 0 e 1
        self._ir = None  # Variabile per memorizzare l'IR caricata
        self._ir_samplerate = None  # Variabile per memorizzare la frequenza di campionamento dell'IR
        self._load_ir()

    def _load_ir(self):
        """
        Carica la Risposta all'Impulso dal percorso specificato.
        """
        try:
            ir_data, sr = sf.read(self.ir_path)

            # Converti in mono se l'IR è stereo (un cabinet ha un'unica IR)
            if ir_data.ndim == 2:
                ir_data = ir_data.mean(axis=1)

            if np.max(np.abs(ir_data)) > 0:
                ir_data /= np.max(np.abs(ir_data))

            self._ir = ir_data
            self._ir_samplerate = sr
            print(f"IR del cabinet caricata con successo da {self.ir_path}.")

        except FileNotFoundError:
            raise FileNotFoundError(f"File IR non trovato al percorso: {self.ir_path}")
        except Exception as e:
            raise IOError(f"Errore nel caricamento del file IR: {e}")

    def apply_effect(self, audio_signal: np.ndarray, samplerate: int, channel_mode: str = 'both') -> np.ndarray:
        """
        Applica l'effetto di cabinet tramite convoluzione.

        Parametri in input:
        - audio_signal: Il segnale audio da processare.
        - samplerate: La frequenza di campionamento del segnale audio.
        - channel_mode: Specifica quali canali devono essere elaborati ('both', 'right', 'left').

        Parametri in output:
        - processed_signal: Il segnale audio con l'effetto di cabinet applicato.
        """
        if self._ir is None:
            raise RuntimeError("Risposta all'Impulso (IR) non caricata. Chiamare _load_ir() o controllare il percorso.")

        ir_to_use = self._ir.copy()

        if samplerate != self._ir_samplerate:
            print(
                f"Attenzione: Frequenza di campionamento del segnale ({samplerate} Hz) diversa dall'IR ({self._ir_samplerate} Hz). "
                "Attuo il resampling...")
            num = samplerate
            den = self._ir_samplerate
            ir_to_use = resample_poly(ir_to_use, num, den)

        original_signal = audio_signal.copy()
        processed_signal = original_signal.copy()

        if audio_signal.ndim == 1:
            processed_effect = self._process_mono(audio_signal, ir_to_use)
            # Taglia il segnale processato alla lunghezza originale (la convoluzione lo allunga)
            processed_effect = processed_effect[:len(audio_signal)]

            processed_signal = (1 - self.mix) * original_signal + self.mix * processed_effect

        elif audio_signal.ndim == 2:

            if channel_mode == 'both' or channel_mode == 'left':
                processed_left = self._process_mono(audio_signal[:, 0], ir_to_use)
                processed_left = processed_left[:len(audio_signal)]
                processed_signal[:, 0] = (1 - self.mix) * original_signal[:, 0] + self.mix * processed_left

            if channel_mode == 'both' or channel_mode == 'right':
                processed_right = self._process_mono(audio_signal[:, 1], ir_to_use)
                processed_right = processed_right[:len(audio_signal)]
                processed_signal[:, 1] = (1 - self.mix) * original_signal[:, 1] + self.mix * processed_right

            elif channel_mode not in ['both', 'left', 'right']:
                raise ValueError("Modalità canale non valida. Scegli tra 'both', 'left', o 'right'.")

        else:
            raise ValueError("Formato audio non supportato. Il segnale deve essere 1D (mono) o 2D (stereo).")

        max_val = np.max(np.abs(processed_signal))
        if max_val > 0:
            processed_signal /= max_val

        return processed_signal

    @staticmethod
    def _process_mono(signal: np.ndarray, ir: np.ndarray) -> np.ndarray:
        """
        Metodo helper statico per l'elaborazione mono tramite convoluzione.
        """
        return fftconvolve(signal, ir, mode='full')