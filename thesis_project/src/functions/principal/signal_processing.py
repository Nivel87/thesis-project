from thesis_project.src.effects import *
from thesis_project.src.functions.principal.user_interaction import get_pan_choice
from thesis_project.src.functions.utility.file_handler import *

def process_audio_file(input_file_path, audio_input, samplerate, effect: AudioEffect, selected_preset: str, selected_channel_mode: str) -> tuple[np.ndarray, np.ndarray, int] | None:
    """
        Applica un effetto audio a un file e restituisce i segnali e il samplerate.

        Parametri in input:
        - input_file_path: Path del file audio.
        - audio_input: file audio.
        - samplerate: samplerate del audio.
        - effect: l'effetto da applicare.
        - selected_preset: il nome del preset di parametri con i quali applicare l'effetto.

        Parametri in output:
        - audio_input, processed_audio, samplerate: segnale di ingresso, segnale processato, frequenza di campionamento
    """
    print(f"Applicazione dell'effetto {type(effect).__name__} con il preset '{selected_preset}' e la modalità '{selected_channel_mode}'...")
    processed_audio = effect.apply_effect(audio_input, samplerate, selected_channel_mode)
    print("Effetto applicato con successo.")

    #equal power pan con squareroot
    try:
        processed_audio = apply_equal_power_pan(processed_audio)
    except ValueError as e:
        print(f"Errore di Panning: {e}. Il Panning è stato saltato.")

    #crea output
    get_output_file(input_file_path, audio_input, effect, selected_preset, selected_channel_mode, processed_audio, samplerate)

    return audio_input, processed_audio, samplerate


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