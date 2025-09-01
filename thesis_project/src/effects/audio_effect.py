from abc import ABC, abstractmethod
import numpy as np

class AudioEffect(ABC):
    """
    Classe base astratta per un effetto audio.
    """
    @abstractmethod
    def apply_effect(self, audio_signal: np.ndarray, samplerate: int) -> np.ndarray:
        """
        Applica l'effetto audio al segnale fornito.

        Args:
            audio_signal (np.ndarray): Il segnale audio di input.
            samplerate (int): La frequenza di campionamento.

        Returns:
            np.ndarray: Il segnale audio con l'effetto applicato.
        """
        pass