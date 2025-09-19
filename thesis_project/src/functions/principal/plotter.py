import matplotlib.pyplot as plt
import numpy as np

def plot_audio_signals(original_signal: np.ndarray, processed_signal: np.ndarray, effect_name: str):
    """
        Visualizza il segnale originale e quello processato.

        Parametri in input:
        - original_signal: il segnale originale
        - processed_signal: il segnale processato
        - effect_name: il nome dell'effetto applicato al segnale
    """

    plt.figure(figsize=(12, 6))           #12 pollici in lunghezza, 6 pollici in altezza
    plt.subplot(2, 1, 1)            #2 righe e 1 colonna, grafico 1
    plt.title('Segnale Audio Originale')
    plt.plot(original_signal)
    plt.xlabel('Campioni')
    plt.ylabel('Ampiezza')
    plt.grid(True)

    plt.subplot(2, 1, 2)            #2 righe e 1 colonna, grafico 2
    plt.title(f'Segnale Audio con {effect_name}')
    plt.plot(processed_signal)
    plt.xlabel('Campioni')
    plt.ylabel('Ampiezza')
    plt.grid(True)

    plt.tight_layout()
    plt.show()
