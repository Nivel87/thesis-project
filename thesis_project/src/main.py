from thesis_project.src.functions.principal.effect_factory import make_effect
from thesis_project.src.functions.principal.signal_processing import process_audio_file
from thesis_project.src.functions.principal.user_interaction import get_user_choice, get_plot_choice
from thesis_project.src.functions.utility.file_handler import get_audio_file


#equal power panning con squareroot (0-1), converto in %

#ping pong delay

def main():

    # prendi file input
    input_file_path, audio_input, samplerate = get_audio_file()

    # scelta effetto e parametri di applicazione
    selected_effect, selected_preset, selected_parameters, selected_channel_mode = get_user_choice()
    if not selected_effect or not selected_preset or not selected_parameters or not selected_channel_mode:
        return

    # X TEST!!!
    # selected_effect = 'cabinet'
    # selected_preset = 'g12t75_4x12'
    # selected_channel_mode = 'both'

    # prendi i parametri scelti e costruisci l'effetto
    effect = make_effect(selected_effect, selected_parameters)
    if not effect:
        print("Errore nella creazione dell'effetto.")
        return

    # processa il file audio
    result = process_audio_file(input_file_path, audio_input, samplerate, effect, selected_preset, selected_channel_mode)
    if result is None:
        return

    # produci il grafico dei segnali in/out e confrontali
    original_signal, processed_signal, _ = result
    get_plot_choice(original_signal, processed_signal, type(effect).__name__)

if __name__ == "__main__":
    main()