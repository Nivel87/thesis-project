from thesis_project.src.functions.principal.effect_factory import build_chain_effect
from thesis_project.src.functions.principal.signal_processing import process_audio_chain
from thesis_project.src.functions.principal.user_interaction import get_plot_choice
from thesis_project.src.functions.utility.file_handler import get_audio_file


def main():

    # prendi file input
    input_file_path, audio_input, samplerate = get_audio_file()

    # costruisci la catena di effetti
    chain_result = build_chain_effect()
    if chain_result is None:
        print("Nessuna catena di effetti da elaborare. Uscita.")
        return
    else:
        effect_chain, effect_display_names = chain_result

    # processa il file audio
    result = process_audio_chain(input_file_path, audio_input, samplerate, effect_chain)
    if result is None:
        return

    # produci il grafico dei segnali in/out e confrontali
    original_signal, processed_signal = result
    get_plot_choice(original_signal, processed_signal, effect_display_names)

if __name__ == "__main__":
    main()