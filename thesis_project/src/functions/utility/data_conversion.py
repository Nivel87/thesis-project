from thesis_project.src.exceptions.custom_exceptions import GoBack
from typing import Callable, Any

def get_validated_input(prompt: str, validator_func: Callable[[Any], bool], error_msg: str, expected_type: type = float) -> Any:
    """
    Richiede un input all'utente, lo converte nel tipo specificato e lo convalida.

    Parametri in input:
    - prompt: stringa visualizzata all'utente.
    - validator_func: funzione di convalida.
    - error_msg: messaggio di errore.
    - expected_type: il tipo di dato atteso (es. float, int).

    Parametri in output:
    - Il valore convalidato.
    """
    while True:
        user_input = input(prompt)
        if user_input.strip() == '-1':
            raise GoBack("Torno al menu precedente.")

        try:
            # Converte l'input nel tipo atteso (float o int)
            value = expected_type(user_input)
            if validator_func(value):
                return value
            else:
                print(error_msg)
        except ValueError:
            print(f"Input non valido. Inserisci un numero del tipo {expected_type.__name__}.")