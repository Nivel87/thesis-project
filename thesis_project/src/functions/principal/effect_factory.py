from thesis_project.src.built_in.presets import EFFECT_REGISTRY
from thesis_project.src.effects import *

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
    # print(f"{selected_params}: {selected_params}")
    if not selected_params:
        return None

    # Infine, crea l'istanza dell'effetto appropriato
    if selected_effect == "reverb":
        return ReverbEffect(**selected_params)
    elif selected_effect == "delay":
        return DelayEffect(**selected_params)
    elif selected_effect == "cabinet":
        return CabinetEffect(**selected_params)
    else:
        raise ValueError(f"Effetto '{selected_effect}' non riconosciuto.")