from thesis_project.src.effects import *
from thesis_project.src.functions.utility.file_handler import *

def process_audio_file(input_file_path, audio_input, samplerate, effect: AudioEffect, selected_preset: str, selected_channel_mode: str) -> tuple[np.ndarray, np.ndarray, int] | None:
    """
        Applica un effetto audio a un file e restituisce i segnali e il samplerate.

        Parametri in input:
        - input_file_path: Path del file audio.
        - audio_input: file audio.
        - samplerate: samplerate del audio.
        - effect: l'effetto da applicare.
        - selected_preset: il nome del preset di parametri con i quali applicare l'effetto.

        Parametri in output:
        - audio_input, processed_audio, samplerate: segnale di ingresso, segnale processato, frequenza di campionamento
    """
    print(f"Applicazione dell'effetto {type(effect).__name__} con il preset '{selected_preset}' e la modalità '{selected_channel_mode}'...")
    processed_audio = effect.apply_effect(audio_input, samplerate, selected_channel_mode)
    print("Effetto applicato con successo.")

    #crea output
    get_output_file(input_file_path, audio_input, effect, selected_preset, processed_audio, samplerate)

    return audio_input, processed_audio, samplerate