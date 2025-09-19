from thesis_project.src.functions.principal.effect_factory import make_effect
from thesis_project.src.functions.principal.signal_processing import process_audio_file
from thesis_project.src.functions.principal.user_interaction import get_user_choice
from thesis_project.src.functions.principal.plotter import plot_audio_signals

#equal power panning con squareroot (0-1), converto in %

# prevedere gli effetti in stereo
#se il file è mono, ho un [1xn] campioni, lo replico sull'altro canale
#se stereo ok
#posso applicare effetti separati sui singoli canali
#ping pong delay
#posso chiedere all'utente se stereo oppure mono

#funzioni che approx risposte all'impulso (chebyshev) x cabinet.
#min errore quadratico medio
#NB occhio a samplerate!


def main():

    # scelta utente
    selected_effect, selected_preset = get_user_choice()
    if not selected_effect or not selected_preset:
        return

    # X TEST!!!
    # selected_effect = 'reverb'
    # selected_preset = 'piccola_stanza'

    # prendi i parametri scelti e costruisci l'effetto
    effect = make_effect(selected_effect, selected_preset)
    if not effect:
        print("Errore nella creazione dell'effetto.")
        return

    # processa il file audio
    result = process_audio_file(effect, selected_preset)
    if result is None:
        return

    # produce il grafico dei segnali in/out e li confronta
    original_signal, processed_signal, _ = result
    plot_audio_signals(original_signal, processed_signal, type(effect).__name__)

if __name__ == "__main__":
    main()