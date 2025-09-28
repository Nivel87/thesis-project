from typing import Dict
from thesis_project.src.functions.utility.data_conversion import get_validated_input
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
IR_CABINET_PATH = BASE_DIR / "ir_cabinet"

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
        "Il numero di riflessioni deve essere un valore positivo.",
        expected_type=int
    )

    decay_rate = get_validated_input(
        "Inserisci il tempo di decadimento (s): ",
        lambda x: x >= 0,
        "Il tempo di decadimento deve essere un valore positivo."
    )

    mix = get_validated_input(
        "Inserisci il mix dry/wet (valore tra 0.0 e 1.0): ",
        lambda x: 0.0 <= x <= 1.0,
        "Valore non valido. Il mix deve essere tra 0.0 e 1.0."
    )

    return {"t60": t60, "num_reflections": num_reflections, "decay_rate": decay_rate, "mix": mix}


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

def get_ping_pong_params() -> Dict[str, float]:
    """
        Costruisce un preset custom per il ritardo Ping Pong Asimmetrico.

        Parametri in output:
        - {"delay_time_l": delay_time_l, "delay_time_r": delay_time_r, "feedback": feedback, "mix": mix}
    """
    print("\nInserisci i parametri per il Ping Pong Ritardo Asimmetrico personalizzato:")

    delay_time_l = get_validated_input(
        "Inserisci il tempo di ritardo L->R (s): ",
        lambda x: x >= 0,
        "Il tempo di ritardo deve essere un valore positivo."
    )

    delay_time_r = get_validated_input(
        "Inserisci il tempo di ritardo R->L (s): ",
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

    return {"delay_time_l": delay_time_l, "delay_time_r": delay_time_r, "feedback": feedback, "mix": mix}


def get_cabinet_params() -> Dict[str, str | float]:
    """
        Costruisce un preset custom per il cabinet, a partire dai dati inseriti dall'utente.

        Parametri in output:
        - {"ir_path": ir_path, "mix": mix} : dizionario che rappresenta il preset
    """
    ir_files = [p.name for p in IR_CABINET_PATH.glob('*.wav') if p.is_file()]
    if not ir_files:
        print(f"ERRORE: Nessun file IR trovato nella cartella: {IR_CABINET_PATH}")
        raise FileNotFoundError("Nessun file IR disponibile per il cabinet custom.")

    print("\nInserisci i parametri per la simulazione Cabinet personalizzata:")
    print("\nFile IR disponibili nella cartella 'ir_cabinet':")
    for i, name in enumerate(ir_files):
        print(f"{i + 1}. {name}")

    selected_index = get_validated_input(
        f"Seleziona il numero del file IR: ",
        lambda x: 1 <= x <= len(ir_files),
        f"Selezione non valida. Inserisci un numero tra 1 e {len(ir_files)}."
    )
    ir_name = ir_files[int(selected_index) - 1]

    mix = get_validated_input(
        "Inserisci il mix dry/wet (valore tra 0.0 e 1.0): ",
        lambda x: 0.0 <= x <= 1.0,
        "Valore non valido. Il mix deve essere tra 0.0 e 1.0."
    )

    return {"ir_name": ir_name, "mix": mix}


# La mappa principale che registra tutti gli effetti
EFFECT_REGISTRY = {
    "reverb": {
        "presets": {
            "piccola_stanza": {"t60": 0.3, "num_reflections": 1500, "decay_rate": 0.5, "mix": 0.3},
            "sala_concerto": {"t60": 0.8, "num_reflections": 3000, "decay_rate": 0.8, "mix": 0.6},
            "cattedrale": {"t60": 5.0, "num_reflections": 5000, "decay_rate": 1.0, "mix": 0.8},
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
    },
    "ping_pong": {
        "presets": {
            "standard": {"delay_time_l": 0.3, "delay_time_r": 0.2, "feedback": 0.7, "mix": 0.8},
        },
        "name": "Ping Pong Delay",
        "get_custom_parameters_func": get_ping_pong_params
    },
    "cabinet": {
        "presets": {
            "cenzo_celestion_v30": {"ir_name": "cenzo_celestion_v30.wav", "mix": 1.0},
            "g12t75_4x12": {"ir_name": "G12T75-4x12.wav", "mix": 1.0},
            "v30_1x12": {"ir_name": "V30-4x12.wav", "mix": 1.0},
        },
        "name": "Cabinet Speaker Simulator",
        "get_custom_parameters_func": get_cabinet_params
    }
}

AVAILABLE_EFFECTS = list(EFFECT_REGISTRY.keys())