from typing import Dict
from thesis_project.src.functions.utility.data_conversion import get_validated_input

def get_reverb_params() -> Dict[str, float]:
    """
        Costruisce un preset custom per il riverbero, a partire dai dati inseriti dall'utente.

        Parametri in output:
        - {"t60": t60, "num_reflections": num_reflections, "decay_rate": decay_rate} : dizionario che rappresenta il preset
    """
    print("\nInserisci i parametri per il Riverbero personalizzato:")

    t60 = get_validated_input(
        "Inserisci il T60 (s): ",
        lambda x: x >= 0,
        "Il T60 deve essere un valore positivo."
    )

    num_reflections = get_validated_input(
        "Inserisci il numero di riflessioni: ",
        lambda x: x >= 0,
        "Il numero di riflessioni deve essere un valore positivo."
    )

    decay_rate = get_validated_input(
        "Inserisci il tempo di decadimento (s): ",
        lambda x: x >= 0,
        "Il tempo di decadimento deve essere un valore positivo."
    )

    return {"t60": t60, "num_reflections": num_reflections, "decay_rate": decay_rate}


def get_delay_params() -> Dict[str, float]:
    """
        Costruisce un preset custom per il ritardo, a partire dai dati inseriti dall'utente.

        Parametri in output:
        - {"delay_time": delay_time, "feedback": feedback, "mix": mix} : dizionario che rappresenta il preset
    """
    print("\nInserisci i parametri per il Ritardo personalizzato:")

    delay_time = get_validated_input(
        "Inserisci il tempo di ritardo (s): ",
        lambda x: x >= 0,
        "Il tempo di ritardo deve essere un valore positivo."
    )

    feedback = get_validated_input(
        "Inserisci il feedback (valore tra 0.0 e 1.0): ",
        lambda x: 0.0 <= x <= 1.0,
        "Valore non valido. Il feedback deve essere tra 0.0 e 1.0."
    )

    mix = get_validated_input(
        "Inserisci il mix (valore tra 0.0 e 1.0): ",
        lambda x: 0.0 <= x <= 1.0,
        "Valore non valido. Il mix deve essere tra 0.0 e 1.0."
    )

    return {"delay_time": delay_time, "feedback": feedback, "mix": mix}


# La mappa principale che registra tutti gli effetti
EFFECT_REGISTRY = {
    "reverb": {
        "presets": {
            "piccola_stanza": {"t60": 0.3, "num_reflections": 1500, "decay_rate": 0.5},
            "sala_concerto": {"t60": 0.8, "num_reflections": 3000, "decay_rate": 0.8},
            "cattedrale": {"t60": 5.0, "num_reflections": 5000, "decay_rate": 1.0},
        },
        "name": "Riverbero",
        "get_custom_parameters_func": get_reverb_params
    },
    "delay": {
        "presets": {
            "slapback": {"delay_time": 0.1, "feedback": 0.3, "mix": 0.4},
            "long_delay": {"delay_time": 1.5, "feedback": 0.7, "mix": 0.7},
        },
        "name": "Ritardo",
        "get_custom_parameters_func": get_delay_params
    }
}


# La lista degli effetti disponibili, ottenuta dinamicamente dalla mappa
AVAILABLE_EFFECTS = list(EFFECT_REGISTRY.keys())