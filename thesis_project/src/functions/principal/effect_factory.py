from pathlib import Path
from thesis_project.src.built_in.presets import EFFECT_REGISTRY
from thesis_project.src.effects import *

def make_effect(selected_effect: str, selected_preset: str, base_path: Path = None) -> AudioEffect | None:
    """
        Crea l'istanza dell'effetto e ne recupera i parametri dai preset definiti.

        Parametri in input:
        - selected_effect: il nome dell'effetto da applicare
        - selected_preset: il nome del preset di parametri con i quali applicare l'effetto
        - base_path: il path contenente le risposte impulsive (solo per Cabinet)

        Parametri in output:
        - AudioEffect | None : l'oggetto AudioEffect costruito con il preset di parametri
    """

    presets = EFFECT_REGISTRY.get(selected_effect, {}).get("presets")
    #print(f"{selected_effect}: {presets}")
    if not presets:
        return None

    params = presets.get(selected_preset)
    #print(f"{selected_preset}: {params}")
    if not params:
        return None

    # Infine, crea l'istanza dell'effetto appropriato
    if selected_effect == "reverb":
        return ReverbEffect(**params)
    elif selected_effect == "delay":
        return DelayEffect(**params)

    return None