import soundfile as sf
import matplotlib.pyplot as plt
import numpy as np

def in_test():
    FILE_AUDIO = r'C:\Users\elede\PycharmProjects\PythonProject\thesis_project\data\input_audio.wav'

    try:
        data, samplerate = sf.read(FILE_AUDIO)

        print(f"File caricato: {FILE_AUDIO}")
        print(f"Sample Rate (sr): {samplerate} Hz")

        n_canali = 1 if len(data.shape) == 1 else data.shape[1]

        print(f"Numero di canali rilevati: {n_canali}")

        n_campioni = len(data) if n_canali == 1 else len(data[:, 0])
        durata_totale = n_campioni / samplerate
        tempo = np.linspace(0, durata_totale, num=n_campioni)


        if n_canali == 1:
            # --- Caso MONO ---
            plt.figure(figsize=(14, 5))
            plt.plot(tempo, data, color='purple')
            plt.title(f'Forma d\'onda Audio Mono')
            plt.xlabel('Tempo (secondi)')
            plt.ylabel('Ampiezza')
            plt.grid(True)
            plt.tight_layout()

        elif n_canali >= 2:
            plt.figure(figsize=(14, 5))

            # Colori da usare per i canali
            colori = ['blue', 'red', 'green', 'orange']

            for i in range(n_canali):
                canale_dati = data[:, i]
                colore = colori[i % len(colori)]

                # Aggiunge il canale corrente allo stesso grafico
                # Aggiunge 'label' per la legenda
                if i == 0:
                    etichetta = 'Canale Sinistro'
                elif i == 1:
                    etichetta = 'Canale Destro'
                else:
                    etichetta = f'Canale {i + 1}'

                plt.plot(tempo, canale_dati, color=colore, label=etichetta, alpha=0.7)

            # Impostazioni del grafico unico
            plt.title('Forma d\'onda Segnale di ingresso', fontsize=16)
            plt.xlabel('Tempo (secondi)')
            plt.ylabel('Ampiezza')
            plt.grid(True)
            plt.legend()  # Mostra la legenda per distinguere i canali
            plt.tight_layout()

        plt.show()


    except FileNotFoundError:
        print(f"ERRORE: File non trovato all'indirizzo '{FILE_AUDIO}'.")
        print("Assicurati che il percorso sia corretto.")
    except Exception as e:
        print(f"Si e' verificato un errore durante l'elaborazione dell'audio: {e}")