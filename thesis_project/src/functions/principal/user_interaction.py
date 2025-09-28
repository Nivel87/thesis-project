from pathlib import Path
from typing import Union

import numpy as np

from thesis_project.src.exceptions.custom_exceptions import GoBack
from thesis_project.src.built_in.presets import EFFECT_REGISTRY, AVAILABLE_EFFECTS
from thesis_project.src.functions.principal.plotter import plot_audio_signals
from thesis_project.src.functions.utility.data_conversion import get_validated_input


def get_input_file_choice(data_path, audio_files) -> Union[Path, None]:
    """
        Consente all'utente di selezionare un file audio da una lista di file .wav trovati in una specifica directory

        Parametri in input:
        - data_path: Il percorso della directory contenente i file audio.
        - audio_files: Una lista di oggetti Path che rappresentano i file audio disponibili.

        Parametri in output:
        - selected_file_path: Il percorso del file selezionato, oppure None
    """
    if not audio_files:
        print(f"Errore: Nessun file audio WAV trovato nella cartella '{data_path}'.")
        print("Assicurati di inserire almeno un file WAV e riavvia il programma.")
        return None

    print("\nScegli un file audio da elaborare:")
    for i, file_path in enumerate(audio_files, 1):
        print(f"{i}. {file_path.name}")

    while True:
        try:
            choice = input("Inserisci il numero del file: ")
            choice_index = int(choice)

            if 1 <= choice_index <= len(audio_files):
                selected_file_path = audio_files[choice_index - 1]
                break
            else:
                print("Scelta non valida. Inserisci un numero corrispondente a un file.")
        except ValueError:
            print("Input non valido. Inserisci un numero.")

    return selected_file_path


def get_effect_choice(is_first_effect: bool) -> Union[str, None]:
    """
        Richiede all'utente di scegliere un effetto (reverb o delay) e restituisce il nome dell'effetto selezionato.

        Parametri in output:
        - AVAILABLE_EFFECTS[choice_index - 1] : il nome dell'effetto selezionato.
    """
    options_count = len(AVAILABLE_EFFECTS)

    while True:
        print("\nQuale effetto vuoi applicare?")
        if is_first_effect:
            print(f"0. Esci dal Programma")
        else:
            print(f"0. Continua con la Catena (non aggiungere altri effetti)")

        for i, effect_name in enumerate(AVAILABLE_EFFECTS, 1):
            effect_details = EFFECT_REGISTRY.get(effect_name, {})
            display_name = effect_details.get("name", effect_name.capitalize())
            print(f"{i}. {display_name} ({effect_name.capitalize()})")

        choice = input("Inserisci il numero dell'effetto: ")

        try:
            choice_index = int(choice)

            if choice_index == 0:
                if is_first_effect:
                    return None
                else:
                    return "DONE_CHAIN"
            # Scelta effetto standard
            elif 1 <= choice_index <= options_count:
                return AVAILABLE_EFFECTS[choice_index - 1]
            else:
                print("Scelta non valida. Riprova.")
        except ValueError:
            print("Scelta non valida. Inserisci un numero.")


def get_preset_choice(effect: str) -> str:
    """
        Richiede all'utente di scegliere un preset per l'effetto specificato.

        Parametri in input:
        - effect: nome dell'effetto da applicare

        Parametri in output:
        - presets[choice_index - 1] oppure "custom" : preset per l'effetto specificato.
    """
    presets = list(EFFECT_REGISTRY[effect]["presets"].keys())

    while True:
        print(f"\nScegli un preset per il {effect.capitalize()}:")
        print("0. Torna indietro")
        for i, preset_name in enumerate(presets, 1):
            print(f"{i}. {preset_name}")
        print(f"{len(presets) + 1}. custom")

        choice = input(f"Inserisci il numero del preset: ")

        if choice == '0':
            raise GoBack("Torno al menu di selezione dell'effetto")

        if choice.lower() == "custom":
            return "custom"

        try:
            choice_index = int(choice)
            if 1 <= choice_index <= len(presets):
                return presets[choice_index - 1]
            elif choice_index == len(presets) + 1:
                return "custom"
            else:
                raise ValueError
        except ValueError:
            print("Selezione del preset non valida. Riprova.")


def get_custom_parameters_choice(effect: str) -> dict[str, float]:
    """
        Richiede all'utente di inserire i parametri per l'opzione "custom" a seconda dell'effetto selezionato.

        Parametri in input:
        - effect: nome dell'effetto da applicare

        Parametri in output:
        - EFFECT_REGISTRY[effect]["get_custom_parameters_func"]() : attraverso la funzione get_custom_parameters_func, si crea il preset
                                                                    per l'opzione "custom" a seconda dell'effetto
    """
    print("\nDigita '-1' in qualsiasi momento per tornare al menu precedente.")
    return EFFECT_REGISTRY[effect]["get_custom_parameters_func"]()


def get_user_choice(is_first_effect: bool = True) -> tuple[str, str, dict[str, float | str], str] | None:
    """
        Gestisce il flusso completo della selezione, guidando l'utente prima nella scelta dell'effetto, poi del preset.

        Parametri in output:
        - effect, parameters | preset: nome dell'effetto da applicare, dizionario di parametri (caso custom) | nome preset.
    """
    while True:
        effect = get_effect_choice(is_first_effect)

        if effect is None:
            return None  # Esci dal programma (prima iterazione)

        if effect == "DONE_CHAIN":
            return None  # Termina la catena (dalla seconda iterazione in poi)

        while True:
            try:
                preset = get_preset_choice(effect)

                if preset == "custom":
                    parameters = get_custom_parameters_choice(effect)
                else:
                    parameters = EFFECT_REGISTRY[effect]["presets"][preset]

                channel_mode = get_channel_mode_choice()
                return effect, preset, parameters, channel_mode
            except GoBack as e:
                error_message = str(e)

                # CASO 1: Ritorno dalla selezione PRESET (Opzione 0)
                if "Torno al menu di selezione dell'effetto" in error_message:
                    print("Tornato alla selezione dell'effetto.")
                    break

                # CASO 2: Ritorno dai CUSTOM PARAMETERS (-1) o da CHANNEL MODE (0)
                elif "Ritorno alla selezione del preset" in error_message:
                    print("Tornato alla selezione del preset.")
                    continue

                else:
                    # Gestione di GoBack non previsto (Fallback) - DEVE ESSERE QUASI IMPOSSIBILE DA RAGGIUNGERE ORA
                    print(f"Eccezione di ritorno non gestita: {error_message}. Torno all'effetto.")
                    break


def get_playback_choice(mode: str) -> str:
    """
        Richiede all'utente le opzioni di riproduzione audio e restituisce la scelta.

        Parametri in input:
        - mode: 'input_only' per la riproduzione del solo audio di input, 'output_comparison' per le opzioni di confronto.

        Parametri in output:
        - str: opzione di riproduzione audio.
    """
    if mode == "input_only":
        print("\nVuoi ascoltare l'audio di input appena caricato?")
        print("1. Sì")
        print("2. No")

        while True:
            choice = input("Seleziona un'opzione: ")
            if choice == '1':
                return 'input'
            elif choice == '2':
                return 'none'
            else:
                print("Scelta non valida. Inserisci 1 o 2.")

    elif mode == "output_comparison":
        print("\nOpzioni di riproduzione audio:")
        print("1. Ascolta solo audio di input")
        print("2. Ascolta solo audio processato")
        print("3. Ascolta entrambi (input e poi output) per un confronto")
        print("4. Non riprodurre nulla e continua")

        while True:
            choice = input("Seleziona un'opzione: ")
            if choice == '1':
                return 'input'
            elif choice == '2':
                return 'output'
            elif choice == '3':
                return 'both'
            elif choice == '4':
                return 'none'
            else:
                print("Scelta non valida. Inserisci un numero tra 1 e 4.")
    return "none"

def get_channel_mode_choice() -> str:
    """
        Richiede all'utente di scegliere la modalità del canale per l'applicazione dell'effetto.

        Parametri in output:
        - choice: La stringa che rappresenta il channel_mode ('both', 'left', o 'right').
    """
    print("\nScegli su quale canale applicare l'effetto:")
    print("0. Torna indietro")
    print("1. Entrambi i canali (both)")
    print("2. Solo canale sinistro (left)")
    print("3. Solo canale destro (right)")

    while True:
        choice = input("Inserisci il numero della tua scelta: ")
        if choice == '0':
            raise GoBack("Ritorno alla selezione del preset")
        elif choice == '1':
            return 'both'
        elif choice == '2':
            return 'left'
        elif choice == '3':
            return 'right'
        else:
            print("Scelta non valida. Riprova.")


def get_pan_choice() -> float:
    """
        Richiede all'utente di inserire il valore di Panning (bilanciamento stereo).

        Parametri in output:
        - pan_value: Valore float compreso tra -1.0 (Sinistra) e 1.0 (Destra).
    """
    pan = get_validated_input(
        "Inserisci il valore di Panning (da -1.0 Sinistra a 1.0 Destra, 0.0 Centro): ",
        lambda x: -1.0 <= x <= 1.0,
        "Valore non valido. Il Panning deve essere compreso tra -1.0 e 1.0.",
        allow_negative_one = True
    )

    return pan


def get_plot_choice(original_signal: np.ndarray, processed_signal: np.ndarray, effect_display_names: list[str]):
    """
        Chiede all'utente quale stile di visualizzazione preferisce per i segnali audio stereo.

        Parametri in input:
        - original_signal: Il segnale audio originale.
        - processed_signal: Il segnale audio processato.
        - effect_name: Il nome dell'effetto applicato.
    """
    is_stereo = original_signal.ndim == 2 and original_signal.shape[1] == 2

    if not is_stereo:
        plot_audio_signals(original_signal, processed_signal, effect_display_names)
        return

    print("\nScegli lo stile di visualizzazione:")
    print("1. Grafici separati per i canali (Sinistro/Destro)")
    print("2. Canali sovrapposti sullo stesso grafico")

    choice = input("Inserisci il numero della tua scelta: ")

    if choice == '1':
        plot_audio_signals(original_signal, processed_signal, effect_display_names, stereo_plot_style='separate')
    elif choice == '2':
        plot_audio_signals(original_signal, processed_signal, effect_display_names, stereo_plot_style='overlay')
    else:
        print("Scelta non valida. Verrà utilizzata la visualizzazione predefinita (grafici separati).")
        plot_audio_signals(original_signal, processed_signal, effect_display_names, stereo_plot_style='separate')
