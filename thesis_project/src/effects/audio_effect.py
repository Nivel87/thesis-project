from abc import ABC, abstractmethod
import numpy as np

class AudioEffect(ABC):
    """
    Classe base astratta per un effetto audio.
    """

    @abstractmethod
    def apply_effect(self, audio_signal: np.ndarray, samplerate: int, channel_mode: str = 'both') -> np.ndarray:
        """
        Applica l'effetto audio al segnale fornito.

        Parametri di input:
        - audio_signal: array segnale di input
        - samplerate: La frequenza di campionamento
        - channel_mode: Specifica quali canali devono essere elaborati ('both', 'right', 'left')

        Returns:
            np.ndarray: Il segnale audio con l'effetto applicato.
        """
        pass