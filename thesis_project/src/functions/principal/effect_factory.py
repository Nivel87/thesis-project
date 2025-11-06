from typing import Tuple, List, Dict, Any

from thesis_project.src.built_in.presets import EFFECT_REGISTRY
from thesis_project.src.effects import *
from thesis_project.src.functions.principal.user_interaction import get_user_choice


def make_effect(selected_effect: str, selected_params: dict) -> AudioEffect | None:
    """
        Crea l'istanza dell'effetto e ne recupera i parametri dai preset definiti.

        Parametri in input:
        - selected_effect: il nome dell'effetto da applicare
        - selected_preset: il nome del preset di parametri con i quali applicare l'effetto
        - base_path: il path contenente le risposte impulsive (solo per Cabinet)

        Parametri in output:
        - AudioEffect | None : l'oggetto AudioEffect costruito con il preset di parametri
    """
    if not selected_params:
        return None

    # Infine, crea l'istanza dell'effetto appropriato
    if selected_effect == "reverb":
        return ReverbEffect(**selected_params)
    elif selected_effect == "delay":
        return DelayEffect(**selected_params)
    elif selected_effect == "ping_pong":
        return PingPongDelayEffect(**selected_params)
    elif selected_effect == "cabinet":
        # Passa i parametri direttamente, inclusi 'ir_source' e 'ir_name' o 'ir_model'
        return CabinetEffect(**selected_params)
    else:
        raise ValueError(f"Effetto '{selected_effect}' non riconosciuto.")


def build_chain_effect() -> tuple[list[Any], list[Any]] | None:
    effect_chain = []
    effect_display_names = []

    first_iteration = True

    while True:
        print("\n--- Configurazione Effetto #{} ---".format(len(effect_chain) + 1))

        # scelta effetto e parametri di applicazione
        result  = get_user_choice(is_first_effect=first_iteration)
        if result is None:
            # Se effect_chain è vuota, l'utente ha scelto "Esci dal Programma"
            if not effect_chain:
                print("Uscita dal programma su richiesta dell'utente.")
                return None
            # Se effect_chain NON è vuota, l'utente ha scelto "Continua con la Catena" (dalla seconda iterazione)
            else:
                print("Catena di effetti completata.")
                break  # Esci dal ciclo e restituisci la catena

        # Imposta first_iteration su False dopo il primo passaggio riuscito
        first_iteration = False

        selected_effect, selected_preset, selected_parameters, selected_channel_mode = result

        # Costruisci l'oggetto effetto
        effect_object = make_effect(selected_effect, selected_parameters)
        if not effect_object:
            print("Errore nella creazione dell'effetto.")
            continue

        display_name = EFFECT_REGISTRY.get(selected_effect, {}).get("name", selected_effect)

        if selected_effect == "cabinet":
            ir_source = selected_parameters.get("ir_source")

            if selected_preset == "custom (Bessel)":
                # Caso Custom Bessel: usa il modello e il nome del preset
                ir_model = selected_parameters.get("ir_model", "Sconosciuto")
                display_name = f"Cabinet - Custom Bessel: {ir_model.capitalize()}"
            elif ir_source == "file":
                # Caso Preset Standard (File IR)
                display_name = f"Cabinet - File Preset: {selected_preset}"
            else:
                # Fallback
                display_name = f"Cabinet - {selected_preset}"

        # Aggiungi l'effetto e i suoi parametri alla catena
        effect_chain.append({
            'effect': effect_object,
            'preset': selected_preset,
            'channel_mode': selected_channel_mode
        })
        effect_display_names.append(display_name)

    return effect_chain, effect_display_names