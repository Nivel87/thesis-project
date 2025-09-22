from pathlib import Path
from typing import Union, Any

import numpy as np
import soundfile as sf
import sounddevice as sd
import threading

from thesis_project.src.functions.principal.user_interaction import get_input_file_choice, get_playback_choice

script_dir = Path(__file__).resolve().parent.parent.parent.parent


def _stop_playback():
    """
        Funzione interna per fermare la riproduzione audio.
    """
    sd.stop()

def _wait_for_input_and_set_event(stop_event: threading.Event):
    """
        Funzione eseguita in un thread separato per attendere l'input dell'utente e interrompere la riproduzione.

        Parametri in input:
        - stop_event: evento per interrompere la riproduzione.
    """
    try:
        input()
        _stop_playback()
        stop_event.set()  # Imposta l'evento per segnalare che l'utente ha interrotto
    except EOFError:
        pass

def play_audio_from_choice(choice: str, input_signal: np.ndarray, processed_signal: Union[np.ndarray, None], samplerate: int):
    """
        Riproduce l'audio in base alla scelta dell'utente, permettendo l'interruzione.

        Parametri in input:
        - choice: La scelta dell'utente ('input', 'output', 'both', 'none').
        - input_signal: Il segnale audio di input.
        - processed_signal: Il segnale audio processato.
        - samplerate: La frequenza di campionamento.
    """
    if choice == 'input':
        print("Riproduzione audio di input (Premi INVIO per interrompere)...")
        stop_event = threading.Event()
        sd.play(input_signal, samplerate)
        stop_thread = threading.Thread(target=_wait_for_input_and_set_event, args=(stop_event,))
        stop_thread.start()
        sd.wait()
        if not stop_event.is_set():
            print("\nRiproduzione terminata. Premi INVIO per continuare col programma...")
            stop_thread.join()
        else:
            stop_thread.join()
    elif choice == 'output':
        if processed_signal is not None:
            print("Riproduzione audio processato (Premi INVIO per interrompere)...")
            stop_event = threading.Event()
            sd.play(processed_signal, samplerate)
            stop_thread = threading.Thread(target=_wait_for_input_and_set_event, args=(stop_event,))
            stop_thread.start()
            sd.wait()
            if not stop_event.is_set():
                print("\nRiproduzione terminata. Premi INVIO per continuare col programma...")
                stop_thread.join()
            else:
                stop_thread.join()
    elif choice == 'both':
        print("Riproduzione audio di input (Premi INVIO per interrompere)...")
        stop_event = threading.Event()
        sd.play(input_signal, samplerate)
        stop_thread = threading.Thread(target=_wait_for_input_and_set_event, args=(stop_event,))
        stop_thread.start()
        sd.wait()
        if not stop_event.is_set():
            print("\nRiproduzione terminata. Premi INVIO per continuare col programma...")
            stop_thread.join()
        else:
            stop_thread.join()

        print("\nRiproduzione audio processato (Premi INVIO per interrompere)...")
        if processed_signal is not None:
            stop_event = threading.Event()
            sd.play(processed_signal, samplerate)
            stop_thread = threading.Thread(target=_wait_for_input_and_set_event, args=(stop_event,))
            stop_thread.start()
            sd.wait()
            if not stop_event.is_set():
                print("\nRiproduzione terminata. Premi INVIO per continuare col programma...")
                stop_thread.join()
            else:
                stop_thread.join()
    elif choice == 'none':
        print("Nessuna riproduzione. Continuo...")

def get_stereo_input(file_input) -> Any:
    """
        Verifica se il file caricato è stereo. Se è mono, lo converte in stereo.

        Parametri in input:
        - file_input: file caricato.

        Parametri in output:
        - file_input: il file caricato (stereo), o il file (mono) caricato e convertito in stereo.
    """
    if file_input.ndim == 1:
        print("Il file caricato è MONO.")
        print("Il file verrà convertito in STEREO replicando il canale.")
        file_input = np.stack((file_input, file_input), axis=1)
        # print(f"Il file ora è stereo, la nuova forma è: {file_input.shape}")
    else:
        print("Il file caricato è STEREO.")

    return file_input


def get_audio_file() -> tuple[Path, np.ndarray, int] | None:
    """
        Permette all'utente di selezionare un file audio dalla cartella 'data' e lo carica in memoria.

        Parametri in output:
        - selected_file_path, audio_input, samplerate: il percorso del file selezionato, il file audio e la sua frequenza di campionamento
    """
    data_path = script_dir / "data"

    # Trova tutti i file .wav nella cartella 'data'
    audio_files = sorted(list(data_path.glob("*.wav")))

    selected_file_path = get_input_file_choice(data_path, audio_files)

    #X TEST!!!
    #selected_file_path = data_path / 'guitar_solo.wav'

    try:
        file_input, samplerate = sf.read(selected_file_path)
    except FileNotFoundError:
        print(f"Errore: il file '{selected_file_path}' non è stato trovato.")
        return None
    except Exception as e:
        print(f"Si è verificato un errore durante la lettura del file: {e}")
        return None

    print(f"Caricamento di '{selected_file_path}'...")

    # verifica mono/stereo
    audio_input = get_stereo_input(file_input)

    # Chiede all'utente se vuole ascoltare l'audio di input
    choice = get_playback_choice("input_only")
    play_audio_from_choice(choice, audio_input, None, samplerate)

    return selected_file_path, audio_input, samplerate


def get_output_file(input_file_path, input_audio, effect, selected_preset, processed_audio, samplerate):
    """
        Salva il segnale audio processato in un file all'interno della cartella output.
        Permette all'utente di riprodurre e confrontare l'audio originale con quello processato finché non decide di continuare

        Parametri in input:
        - input_file_path: Il percorso del file di input originale.
        - input_audio: L'array NumPy del segnale audio di input.
        - effect: L'oggetto effetto che è stato applicato al segnale.
        - selected_preset: Il nome del preset utilizzato.
        - processed_audio: L'array NumPy del segnale audio processato.
        - samplerate: La frequenza di campionamento del segnale audio.
    """
    output_dir = script_dir / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Genera il nome del file di output in modo sicuro per evitare sovrascritture
    file_stem = f"{input_file_path.stem}_{type(effect).__name__.lower()}_{selected_preset.replace(' ', '_')}"
    output_path = output_dir / f"{file_stem}.wav"

    counter = 1
    while output_path.exists():
        output_path = output_dir / f"{file_stem}_{counter}.wav"
        counter += 1

    sf.write(output_path, processed_audio, samplerate)

    # Chiede all'utente le opzioni di riproduzione
    while True:
        choice = get_playback_choice("output_comparison")
        play_audio_from_choice(choice, input_audio, processed_audio, samplerate)
        if choice == 'none':
            break

    print(f"File processato salvato in '{output_path}'.")
