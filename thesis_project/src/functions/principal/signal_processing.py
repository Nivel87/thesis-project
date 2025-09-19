from thesis_project.src.effects import *
from thesis_project.src.functions.utility.file_handler import *

def process_audio_file(effect: AudioEffect, selected_preset: str) -> tuple[np.ndarray, np.ndarray, int] | None:
    """
        Applica un effetto audio a un file e restituisce i segnali e il samplerate.

        Parametri in input:
        - effect: l'effetto da applicare
        - selected_preset: il nome del preset di parametri con i quali applicare l'effetto

        Parametri in output:
        - audio_input, processed_audio, samplerate: segnale di ingresso, segnale processato, frequenza di campionamento
    """

    #prendi file input
    input_file_path, audio_input, samplerate = get_audio_file()

    #applica effetto
    print(f"Applicazione dell'effetto {type(effect).__name__} con il preset '{selected_preset}'...")
    processed_audio = effect.apply_effect(audio_input, samplerate)
    print("Effetto applicato con successo.")

    #crea output
    get_output_file(input_file_path, audio_input, effect, selected_preset, processed_audio, samplerate)

    return audio_input, processed_audio, samplerate