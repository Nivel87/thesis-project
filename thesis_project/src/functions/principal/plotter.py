import matplotlib.pyplot as plt
import numpy as np


def plot_audio_signals(original_signal: np.ndarray, processed_signal: np.ndarray, effect_name: str,
                       stereo_plot_style: str = 'separate'):
    """
        Visualizza il segnale originale e quello processato, gestendo sia audio mono che stereo
        e permettendo di scegliere lo stile di visualizzazione per i segnali stereo.

        Parametri in input:
        - original_signal: il segnale originale
        - processed_signal: il segnale processato
        - effect_name: il nome dell'effetto applicato al segnale
        - stereo_plot_style: 'separate' per grafici separati per ogni canale stereo,
                             'overlay' per sovrapporre i canali sullo stesso grafico.
                             Ignorato per segnali mono.
    """
    # Verifica se i segnali sono stereo
    is_stereo = original_signal.ndim == 2 and original_signal.shape[1] == 2

    if is_stereo and stereo_plot_style == 'separate':
        # Opzione 1: Grafici separati per canale
        plt.figure(figsize=(15, 10))

        # Canale sinistro originale
        plt.subplot(2, 2, 1)
        plt.title('Segnale Originale - Canale Sinistro')
        plt.plot(original_signal[:, 0])
        plt.xlabel('Campioni')
        plt.ylabel('Ampiezza')
        plt.grid(True)

        # Canale destro originale
        plt.subplot(2, 2, 2)
        plt.title('Segnale Originale - Canale Destro')
        plt.plot(original_signal[:, 1])
        plt.xlabel('Campioni')
        plt.ylabel('Ampiezza')
        plt.grid(True)

        # Canale sinistro processato
        plt.subplot(2, 2, 3)
        plt.title(f'Segnale {effect_name} - Canale Sinistro')
        plt.plot(processed_signal[:, 0])
        plt.xlabel('Campioni')
        plt.ylabel('Ampiezza')
        plt.grid(True)

        # Canale destro processato
        plt.subplot(2, 2, 4)
        plt.title(f'Segnale {effect_name} - Canale Destro')
        plt.plot(processed_signal[:, 1])
        plt.xlabel('Campioni')
        plt.ylabel('Ampiezza')
        plt.grid(True)

    else:  # include segnali mono e l'opzione 'overlay' per stereo
        # Opzione 2: Sovrapposizione o singolo grafico per mono
        plt.figure(figsize=(12, 6))

        # Grafico del segnale originale
        plt.subplot(2, 1, 1)
        plt.title('Segnale Audio Originale')

        if is_stereo:
            plt.plot(original_signal[:, 0], label='Canale Sinistro')
            plt.plot(original_signal[:, 1], label='Canale Destro')
            plt.legend()
        else:
            plt.plot(original_signal)

        plt.xlabel('Campioni')
        plt.ylabel('Ampiezza')
        plt.grid(True)

        # Grafico del segnale processato
        plt.subplot(2, 1, 2)
        plt.title(f'Segnale Audio con {effect_name}')

        if is_stereo:
            plt.plot(processed_signal[:, 0], label='Canale Sinistro')
            plt.plot(processed_signal[:, 1], label='Canale Destro')
            plt.legend()
        else:
            plt.plot(processed_signal)

        plt.xlabel('Campioni')
        plt.ylabel('Ampiezza')
        plt.grid(True)

    plt.tight_layout()
    plt.show()
