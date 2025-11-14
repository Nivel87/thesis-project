import matplotlib.pyplot as plt
import numpy as np


def build_plot_title(effect_display_names: list[str]) -> str:
    """
    Crea la stringa del titolo gestendo gli indici per gli effetti duplicati.
    Riceve i nomi descrittivi (es. 'Riverbero', 'Ritardo').
    """

    total_counts = {}
    # 1. Pre-calcolo del numero totale di occorrenze di ogni nome (es. 'Riverbero': 2, 'Ritardo': 1)
    for name in effect_display_names:
        total_counts[name] = total_counts.get(name, 0) + 1

    current_counts = {}
    final_names = []

    # 2. Iterazione per costruire la stringa finale con gli indici
    for name in effect_display_names:

        # Aggiorna il conteggio di occorrenze viste finora per questo nome
        current_counts[name] = current_counts.get(name, 0) + 1

        # Aggiungi l'indice SOLO se il nome appare più di una volta in totale
        if total_counts[name] > 1:
            # Aggiunge l'indice (es. 'Riverbero1', 'Ritardo2')
            final_names.append(f"{name}{current_counts[name]}")
        else:
            # Se non ci sono duplicati, usa solo il nome base (es. 'Ritardo')
            final_names.append(name)

    chain_name = ' -> '.join(final_names)
    return f"Segnale Audio con {chain_name}"


def plot_audio_signals(original_signal: np.ndarray, processed_signal: np.ndarray, sampling_rate: int,
                       effect_name: list[str], stereo_plot_style: str = 'separate'):
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
    # 1. Calcola il vettore del tempo in secondi
    num_samples = len(original_signal)
    time = np.linspace(0, num_samples / sampling_rate, num_samples, endpoint=False)

    # Verifica se i segnali sono stereo
    is_stereo = original_signal.ndim == 2 and original_signal.shape[1] == 2

    # Definisce le etichette per gli assi
    x_label = 'Tempo (s)'
    y_label = 'Ampiezza'

    if is_stereo and stereo_plot_style == 'separate':
        # Opzione 1: Grafici separati per canale
        plt.figure(figsize=(15, 10))

        # Canale sinistro originale
        plt.subplot(2, 2, 1)
        plt.title('Segnale Originale - Canale Sinistro')
        plt.plot(time, original_signal[:, 0])
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.grid(True)

        # Canale destro originale
        plt.subplot(2, 2, 2)
        plt.title('Segnale Originale - Canale Destro')
        plt.plot(time, original_signal[:, 1])
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.grid(True)

        # Canale sinistro processato
        plt.subplot(2, 2, 3)
        plt.title(f'Segnale {effect_name} - Canale Sinistro')
        plt.plot(time, processed_signal[:, 0])
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.grid(True)

        # Canale destro processato
        plt.subplot(2, 2, 4)
        plt.title(f'Segnale {effect_name} - Canale Destro')
        plt.plot(time, processed_signal[:, 1])
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.grid(True)

    else:  # include segnali mono e l'opzione 'overlay' per stereo
        # Opzione 2: Sovrapposizione o singolo grafico per mono
        plt.figure(figsize=(12, 6))

        # Grafico del segnale originale
        plt.subplot(2, 1, 1)
        plt.title('Segnale Audio Originale')

        if is_stereo:
            plt.plot(time,original_signal[:, 0], label='Canale Sinistro')
            plt.plot(time,original_signal[:, 1], label='Canale Destro')
            plt.legend()
        else:
            plt.plot(time,original_signal)

        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.grid(True)

        # Grafico del segnale processato
        plt.subplot(2, 1, 2)
        plt.title(f'Segnale Audio con {effect_name}')

        if is_stereo:
            plt.plot(time,processed_signal[:, 0], label='Canale Sinistro')
            plt.plot(time, processed_signal[:, 1], label='Canale Destro')
            plt.legend()
        else:
            plt.plot(time, processed_signal)

        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.grid(True)

    plt.tight_layout()
    plt.show()
