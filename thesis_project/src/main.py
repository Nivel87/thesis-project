from pathlib import Path
import soundfile as sf
import matplotlib.pyplot as plt
import numpy as np

from thesis_project.src.effects.audio_effect import AudioEffect
from thesis_project.src.effects.reverb import ReverbEffect
from thesis_project.src.effects.delay import DelayEffect


def process_audio_file(input_file: str, effect: AudioEffect, selected_preset: str) -> tuple[
                                                                                          np.ndarray, np.ndarray, int] | None:
    """
    Applica un effetto audio a un file e restituisce i segnali e la samplerate.
    """
    # Converti la stringa del percorso in un oggetto Path
    input_file_path = Path(input_file)

    try:
        audio_input, samplerate = sf.read(input_file_path)
    except FileNotFoundError:
        print(f"Errore: il file '{input_file_path}' non è stato trovato.")
        return None
    except Exception as e:
        print(f"Si è verificato un errore durante la lettura del file: {e}")
        return None

    print(f"Caricamento di '{input_file_path}'...")
    print(f"Applicazione dell'effetto {type(effect).__name__} con il preset '{selected_preset}'...")

    processed_audio = effect.apply_effect(audio_input, samplerate)
    print("Effetto applicato con successo.")

    # Genera il nome del file di output in modo sicuro per evitare sovrascritture
    base_output_dir = input_file_path.parent.parent / 'output'
    file_stem = f"{input_file_path.stem}_{type(effect).__name__.lower()}_{selected_preset.replace(' ', '_')}"
    output_path = base_output_dir / f"{file_stem}.wav"

    counter = 1
    while output_path.exists():
        output_path = base_output_dir / f"{file_stem}_{counter}.wav"
        counter += 1

    sf.write(output_path, processed_audio, samplerate)
    print(f"File processato salvato in '{output_path}'.")

    return audio_input, processed_audio, samplerate


def plot_audio_signals(original_signal: np.ndarray, processed_signal: np.ndarray, effect_name: str):
    """
    Visualizza il segnale originale e quello processato.
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


def get_user_choice() -> tuple[str, str] | None:
    """
    Gestisce l'interazione con l'utente per la scelta dell'effetto e del preset.
    """
    reverb_presets = {
        "piccola_stanza": {"t60": 0.8, "num_reflections": 500, "decay_rate": 3.0},
        "sala_concerto": {"t60": 1.5, "num_reflections": 1500, "decay_rate": 5.0},
        "grande_cattedrale": {"t60": 4.0, "num_reflections": 3000, "decay_rate": 8.0}
    }

    delay_presets = {
        "slapback_echo": {"delay_time": 0.08, "feedback": 0.2, "mix": 0.5},
        "long_echo": {"delay_time": 0.5, "feedback": 0.6, "mix": 0.5}
    }

    while True:
        print("\nQuale effetto vuoi applicare?")
        print("1. Riverbero (Reverb)")
        print("2. Ritardo (Delay)")

        choice = input("Inserisci il numero dell'effetto (1 o 2): ")

        if choice == "1":
            selected_effect = "reverb"
            presets = list(reverb_presets.keys())
            break
        elif choice == "2":
            selected_effect = "delay"
            presets = list(delay_presets.keys())
            break
        else:
            print("Scelta non valida. Riprova.")

    while True:
        print(f"\nScegli un preset per il {selected_effect.capitalize()}:")
        for i, preset_name in enumerate(presets, 1):
            print(f"{i}. {preset_name}")

        preset_choice = input("Inserisci il numero del preset: ")

        try:
            preset_index = int(preset_choice)
            if 1 <= preset_index <= len(presets):
                selected_preset = presets[preset_index - 1]
                return selected_effect, selected_preset
            else:
                raise ValueError
        except ValueError:
            print("Selezione del preset non valida. Riprova.")


def get_effect_and_params(selected_effect: str, selected_preset: str) -> AudioEffect | None:
    """
    Crea l'istanza dell'effetto e ne recupera i parametri dai preset definiti.
    """
    presets_map = {
        "reverb": {
            "piccola_stanza": {"t60": 0.8, "num_reflections": 500, "decay_rate": 3.0},
            "sala_concerto": {"t60": 1.5, "num_reflections": 1500, "decay_rate": 5.0},
            "grande_cattedrale": {"t60": 4.0, "num_reflections": 3000, "decay_rate": 8.0}
        },
        "delay": {
            # Un delay molto breve, tipico della musica rockabilly, che produce un'eco singola e secca.
            "slapback_echo": {"delay_time": 0.08, "feedback": 0.2, "mix": 0.5},
            # Un delay più lungo con più ripetizioni, utile per creare un'atmosfera o per "riempire" il suono
            "long_echo": {"delay_time": 0.5, "feedback": 0.6, "mix": 0.5}
        }
    }

    params = presets_map.get(selected_effect, {}).get(selected_preset)
    if not params:
        return None

    if selected_effect == "reverb":
        return ReverbEffect(**params)
    elif selected_effect == "delay":
        return DelayEffect(**params)

    return None


def main():
    """
    Script principale che orchestra il flusso di elaborazione audio.
    """
    base_path = Path(__file__).parent.parent
    input_file = base_path / 'data' / 'guitar_solo.wav'

    output_dir = base_path / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_file.is_file():
        print(f"Errore: il file di input '{input_file}' non è stato trovato.")
        print("Assicurati che il file esista nella cartella 'data' e riavvia il programma.")
        return

    selected_effect, selected_preset = get_user_choice()
    if not selected_effect or not selected_preset:
        return

    effect = get_effect_and_params(selected_effect, selected_preset)
    if not effect:
        print("Errore nella creazione dell'effetto.")
        return

    # Processa il file e ottieni i segnali
    result = process_audio_file(str(input_file), effect, selected_preset)
    if result is None:
        return

    original_signal, processed_signal, _ = result   #unpacking tupla (_ non serve per il plot, contiene la frequenza di campionamento)

    # Passa i segnali alla funzione di plot
    plot_audio_signals(original_signal, processed_signal, type(effect).__name__)

# Questa è la convenzione standard in Python per assicurarsi che il codice all'interno di main() venga eseguito
# solo quando lo script è avviato direttamente e non quando viene importato come modulo in un altro script.
if __name__ == "__main__":
    main()