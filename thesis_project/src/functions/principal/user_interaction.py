from pathlib import Path
from typing import Union

from thesis_project.src.exceptions.custom_exceptions import GoBack
from thesis_project.src.built_in.presets import EFFECT_REGISTRY, AVAILABLE_EFFECTS

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


def get_effect_choice() -> str:
    """
        Richiede all'utente di scegliere un effetto (reverb o delay) e restituisce il nome dell'effetto selezionato.

        Parametri in output:
        - AVAILABLE_EFFECTS[choice_index - 1] : il nome dell'effetto selezionato.
    """
    while True:
        print("\nQuale effetto vuoi applicare?")
        for i, effect_name in enumerate(AVAILABLE_EFFECTS, 1):
            # Ottieni i dettagli dell'effetto usando la chiave
            effect_details = EFFECT_REGISTRY.get(effect_name, {})

            # Estrai il nome descrittivo dell'effetto, se esiste
            display_name = effect_details.get("name", effect_name.capitalize())

            # Stampa nel formato desiderato
            print(f"{i}. {display_name} ({effect_name.capitalize()})")

        choice = input("Inserisci il numero dell'effetto: ")

        try:
            choice_index = int(choice)
            if 1 <= choice_index <= len(AVAILABLE_EFFECTS):
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
        print("0. Torna indietro")  # Aggiungi l'opzione "Torna indietro"
        for i, preset_name in enumerate(presets, 1):
            print(f"{i}. {preset_name}")
        print(f"{len(presets) + 1}. custom")

        choice = input(f"Inserisci il numero del preset: ")

        # Gestisci l'opzione "Torna indietro"
        if choice == '0':
            raise GoBack("Torno al menu precedente")

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


def get_user_choice() -> tuple[str, str | dict[str, float]]:
    """
        Gestisce il flusso completo della selezione, guidando l'utente prima nella scelta dell'effetto, poi del preset.

        Parametri in output:
        - effect, parameters | preset: nome dell'effetto da applicare, dizionario di parametri (caso custom) | nome preset.
    """
    while True:
        effect = get_effect_choice()

        while True:
            try:
                preset = get_preset_choice(effect)

                if preset == "custom":
                    try:
                        parameters = get_custom_parameters_choice(effect)
                        return effect, parameters
                    except GoBack:
                        print("Torno alla selezione del preset.")
                        continue
                else:
                    return effect, preset
            except GoBack:
                print("Tornato alla selezione dell'effetto.")
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
        print("[1] Sì")
        print("[2] No")

        while True:
            choice = input("Seleziona un'opzione [1-2]: ")
            if choice == '1':
                return 'input'
            elif choice == '2':
                return 'none'
            else:
                print("Scelta non valida. Inserisci 1 o 2.")

    elif mode == "output_comparison":
        print("\nOpzioni di riproduzione audio:")
        print("[1] Ascolta solo audio di input")
        print("[2] Ascolta solo audio processato")
        print("[3] Ascolta entrambi (input e poi output) per un confronto")
        print("[4] Non riprodurre nulla e continua")

        while True:
            choice = input("Seleziona un'opzione [1-4]: ")
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