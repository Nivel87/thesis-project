from pathlib import Path

import soundfile as sf
import matplotlib.pyplot as plt
from thesis_project.src.effects.audio_effect import AudioEffect
from thesis_project.src.effects.reverb import ReverbEffect
# Quando avrai un altro effetto, ad esempio un delay, lo importerai qui
# from thesis_project.src.effects.delay import DelayEffect

def process_audio_file(input_file: str, output_file: str, effect: AudioEffect):
    """
    Funzione generica per applicare un effetto audio a un file.
    """
    try:
        audio_input, samplerate = sf.read(input_file)
    except FileNotFoundError:
        print(f"Errore: il file '{input_file}' non è stato trovato.")
        return

    print(f"Caricamento di '{input_file}'...")

    # Applica l'effetto in modo generico
    print(f"Applicazione dell'effetto {type(effect).__name__}...")
    convolved_audio = effect.apply_effect(audio_input, samplerate)
    print("Effetto applicato con successo.")

    # Salva il file processato
    sf.write(output_file, convolved_audio, samplerate)
    print(f"File processato salvato in '{output_file}'.")

    # Visualizzazione dei risultati
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.title('Segnale Audio Originale')
    plt.plot(audio_input)
    plt.xlabel('Campioni')
    plt.ylabel('Ampiezza')
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.title(f'Segnale Audio con {type(effect).__name__}')
    plt.plot(convolved_audio)
    plt.xlabel('Campioni')
    plt.ylabel('Ampiezza')
    plt.grid(True)

    plt.tight_layout()
    plt.show()


def main():
    """
    Script principale per processare i file audio.
    """
    base_path = Path(__file__).parent.parent
    input_file = base_path/'data'/'guitar_solo_input.wav'   #file freesound (modificato con audacity)
    output_file = base_path/'output'/'guitar_solo_reverb_output.wav'

    # Assicurati che la cartella di output esista
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Istanzia l'effetto specifico
    reverb_effect = ReverbEffect(t60=3.0, num_reflections=2000, decay_rate=6.0)

    # Chiama la funzione generica passando l'effetto come argomento
    process_audio_file(str(input_file), str(output_file), reverb_effect)


if __name__ == "__main__":
    main()