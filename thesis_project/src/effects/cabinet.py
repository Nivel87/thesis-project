import numpy as np
from scipy.signal import fftconvolve, resample_poly
import soundfile as sf
from scipy.special import j1
from thesis_project.src.effects.audio_effect import AudioEffect
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
IR_CABINET_PATH = BASE_DIR / "ir_cabinet"

class CabinetEffect(AudioEffect):
    def __init__(self, ir_source: str, mix: float = 1.0, ir_name: str = None, **bessel_params):
        self.ir_source = ir_source
        self.mix = np.clip(mix, 0.0, 1.0)  # Assicura che mix sia tra 0 e 1
        self._ir = None
        self._ir_samplerate = 44100
        self.ir_name = ir_name

        if ir_source == 'file':
            if ir_name is None:
                raise ValueError("ir_name è richiesto per ir_source='file'.")
            self.ir_path = IR_CABINET_PATH / ir_name
            self._load_ir()
        elif ir_source == 'bessel':
            self._generate_ir_bessel(bessel_params)
        else:
            raise ValueError(f"ir_source '{ir_source}' non riconosciuto. Deve essere 'file' o 'bessel'.")


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


    def _generate_ir_bessel(self, bessel_params: dict):
        """
                Genera l'IR sintetica.
                - bessel_params: mappa dei parametri per creare la ir.
                """
        fs = self._ir_samplerate
        kx = bessel_params['kx']
        duration = bessel_params['duration']
        samples = int(fs * duration)

        # Crea l'array del tempo in secondi
        x = np.arange(0, samples) /fs

        # Applica la funzione di Bessel
        y_impulse = j1(kx * x)

        # Normalizzazione
        if np.max(np.abs(y_impulse)) > 0:
            y_impulse /= np.max(np.abs(y_impulse))

        self._ir = y_impulse
        print(f"IR sintetica con funzioni di Bessel generata con successo.")

        return self._ir


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
            print(f"Attenzione: Frequenza di campionamento del segnale ({samplerate} Hz) diversa dall'IR ({self._ir_samplerate} Hz). Attuo il resampling...")
            num = samplerate
            den = self._ir_samplerate
            ir_to_use = resample_poly(ir_to_use, num, den)

        original_signal = audio_signal.copy()
        processed_signal = original_signal.copy()

        if audio_signal.ndim == 1:
            processed_effect = fftconvolve(audio_signal, ir_to_use, mode='full')
            processed_effect = processed_effect[:len(audio_signal)]    # Taglia il segnale processato alla lunghezza originale (la convoluzione lo allunga)
            processed_signal = (1 - self.mix) * original_signal + self.mix * processed_effect
        elif audio_signal.ndim == 2:
            if channel_mode == 'both' or channel_mode == 'left':
                processed_left = fftconvolve(audio_signal[:, 0], ir_to_use, mode='full')
                processed_left = processed_left[:len(audio_signal)]  # Taglio
                processed_signal[:, 0] = (1 - self.mix) * original_signal[:, 0] + self.mix * processed_left

            if channel_mode == 'both' or channel_mode == 'right':
                processed_right = fftconvolve(audio_signal[:, 1], ir_to_use, mode='full')
                processed_right = processed_right[:len(audio_signal)]  # Taglio
                processed_signal[:, 1] = (1 - self.mix) * original_signal[:, 1] + self.mix * processed_right

            elif channel_mode not in ['both', 'left', 'right']:
                raise ValueError("Modalità canale non valida. Scegli tra 'both', 'left', o 'right'.")
        else:
            raise ValueError("Formato audio non supportato. Il segnale deve essere 1D (mono) o 2D (stereo).")

        max_val = np.max(np.abs(processed_signal))
        if max_val > 0:
            processed_signal /= max_val

        return processed_signal