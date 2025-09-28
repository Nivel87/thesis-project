from thesis_project.src.functions.principal.user_interaction import get_pan_choice
from thesis_project.src.functions.utility.file_handler import *

def apply_equal_power_pan(audio_signal: np.ndarray) -> np.ndarray:
    """
    Applica l'equal power panning (curva a radice quadrata) a un segnale stereo.

    Il Pan Law (regola del Pan) garantisce che la potenza percepita rimanga costante
    spostando il segnale tra i canali sinistro e destro.

    Parametri in input:
    - audio_signal: Segnale audio stereo (ndarray 2D) con shape (num_samples, 2).
    - pan: Valore di panning tra -1.0 (hard left) e 1.0 (hard right).

    Parametri in output:
    - processed_signal: Il segnale audio stereo con il panning applicato.
    """
    if audio_signal.ndim != 2 or audio_signal.shape[1] != 2:
        raise ValueError("Il Panning richiede un segnale stereo (ndim=2, 2 canali).")

    pan = get_pan_choice()

    # Normalizzazione del valore di pan: [-1.0, 1.0] -> [0.0, 1.0]
    # theta_norm = 0.0 per Hard Left, 0.5 per Center, 1.0 per Hard Right
    theta_norm = (pan + 1.0) / 2.0

    # Calcolo dei guadagni L e R Pan Law (sin/cos, noto anche come Root-Square)
    # L'angolo varia tra 0 (pi/2 * 0) e pi/2 (pi/2 * 1)
    angle = theta_norm * np.pi / 2

    # Guadagno Sinistro: max quando l'angolo è 0 (cos(0)=1), min quando l'angolo è pi/2 (cos(pi/2)=0)
    gain_l = np.cos(angle)

    # Guadagno Destro: min quando l'angolo è 0 (sin(0)=0), max quando l'angolo è pi/2 (sin(pi/2)=1)
    gain_r = np.sin(angle)

    # Applicazione del guadagno
    processed_signal = audio_signal.copy()

    processed_signal[:, 0] *= gain_l
    processed_signal[:, 1] *= gain_r

    return processed_signal


def process_audio_chain(input_file_path, audio_data, samplerate, effect_chain):
    """
    Applica una sequenza di effetti all'audio di input.

    """
    current_signal = audio_data.copy()
    original_signal = audio_data

    try:
        for i, item in enumerate(effect_chain):
            effect = item['effect']
            channel_mode = item['channel_mode']

            print(f"Applicando l'effetto #{i + 1}: {type(effect).__name__}...")
            processed_block = effect.apply_effect(current_signal, samplerate, channel_mode)

            current_signal = processed_block
    except Exception as e:
        print(f"Errore durante il processing della catena di effetti: {e}")
        return None

    # equal power pan con squareroot
    try:
        current_signal = apply_equal_power_pan(current_signal)
    except ValueError as e:
        print(f"Errore di Panning: {e}. Il Panning è stato saltato.")

    # crea output
    get_output_file(input_file_path, original_signal, current_signal, samplerate)

    return original_signal, current_signal

