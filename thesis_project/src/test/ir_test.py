import numpy as np
from matplotlib import pyplot as plt
from scipy.io import wavfile
from scipy.signal import fftconvolve
from scipy.special import j1

from thesis_project.src.effects import ReverbEffect, DelayEffect, PingPongDelayEffect, CabinetEffect


def ir_reverb_test():
    T60 = 2.0
    NUM_REFLECTIONS = 1000
    DECAY_RATE = 2.0
    MIX = 0.5
    SAMPLERATE = 44100

    reverb = ReverbEffect(T60, NUM_REFLECTIONS, DECAY_RATE, MIX)
    ir = reverb.create_reverb_ir(SAMPLERATE)

    time_axis_samples = np.arange(ir.size)
    time_axis_seconds = time_axis_samples / SAMPLERATE

    plt.figure(figsize=(12, 6))

    plt.plot(time_axis_seconds, ir, linewidth=0.5, label='Risposta all\'Impulso (IR)')

    plt.title(f"Risposta all'Impulso del Riverbero (T60={T60}s, Riflessioni={NUM_REFLECTIONS})")
    plt.xlabel("Tempo (secondi)")
    plt.ylabel("Ampiezza")
    plt.grid(True)
    plt.legend()
    plt.show()

    print(f"Grafico Reverb completato.")

    # plt.savefig('ir_reverb.png', dpi=300)
    # plt.close()


def ir_mono_delay_test():
    """
    Genera la risposta impulsiva per il Delay Mono con Feedback.

    Parametri standard:
    - Delay Time: 0.5 secondi (Eco ritmica media)
    - Feedback: 0.6 (Eco che si spegne gradualmente)
    - Mix: 0.4 (Dry/Wet bilanciato)
    - Samplerate: frequenza di campionamento
    """

    # Parametri standard (slapback echo - effetto rockabilly)
    # Delay molto breve e con pochissime ripetizioni, x dare corpo a voci/chitarre.
    # Crea un'eco singola o doppia che si sente appena dopo l'originale, fondendosi per ispessire il suono.
    #delay_time = 0.1
    #feedback = 0.2
    #mix = 0.3
    #samplerate = 44100

    # Parametri standard (delay ritmico - eco di ripetizione)
    # Crea ripetizioni chiare e distinte che seguono il ritmo e che svaniscono gradualmente.
    delay_time = 0.5 #(dipende dal bpm del brano: delay_time=(60000/bpm)*frazione_ritmica . Se p.e. ho durata 1/4, frazione_ritmica=4
    feedback = 0.6
    mix = 0.4
    samplerate = 44100

    # Parametri standard (delay spaziale - eco lunga e sognante)
    # Usato per creare texture ambientali, spazi ampi o dissolvenze lunghe. Spesso ha un tempo lungo e un feedback elevato.
    # delay_time = 1.1
    # feedback = 0.8
    # mix = 0.8 (se 1, si sente solo l'eco)
    # samplerate = 44100

    duration_sec_plot = 3.0

    delay_mono = DelayEffect(delay_time, feedback, mix)

    ir_signal_mono = delay_mono.create_delay_ir(samplerate, duration_seconds=duration_sec_plot)

    print("Generazione e test IR Delay Mono con Feedback completata.")
    print(f"Parametri: Tempo={delay_time}s, Feedback={feedback}, Mix={mix}, Samplerate={samplerate}")
    print(f"Durata visualizzata: {duration_sec_plot:.2f}s")

    time_axis = np.arange(len(ir_signal_mono)) / samplerate

    plt.figure(figsize=(10, 4))
    plt.stem(time_axis, ir_signal_mono, linefmt='b-', markerfmt='bo', basefmt="r-")

    plt.title(f"Risposta Impulsiva Delay Mono (T={delay_time}s, F={feedback}, M={mix})")
    plt.xlabel("Tempo (s)")
    plt.xlim(0, duration_sec_plot)
    plt.ylabel("Ampiezza Normalizzata")
    plt.grid(True, linestyle='--')
    plt.tight_layout()
    plt.show()

    print(f"Grafico IR Delay Mono completato.")

    # plt.savefig('ir_delay_mono.png', dpi=300)
    # plt.close()


def ir_ping_pong_test():
    """
    Genera la risposta impulsiva per il Ping Pong Delay Asimmetrico.

    Parametri standard:
    - Delay Time L (L->R): 0.3 secondi
    - Delay Time R (R->L): 0.5 secondi (Asimmetrico per effetto "ping-pong")
    - Feedback: 0.75 (Feedback più alto per un effetto più evidente)
    - Mix: 0.8 (Più Wet per focalizzare l'attenzione sul "rimbalzo")
    """
    # Parametri BPM (60 BPM -> 1 Croma = 0.5s)
    BPM = 60
    T_Eighth_Note = 60 / BPM / 2  # 0.5 secondi

    # Parametri del delay
    delay_time_l = T_Eighth_Note  # 0.5s
    delay_time_r = T_Eighth_Note  # 0.5s
    feedback = 0.75
    mix = 0.8
    samplerate = 44100
    duration_sec_plot = 4.0

    pp_delay = PingPongDelayEffect(
        delay_time_l=delay_time_l,
        delay_time_r=delay_time_r,
        feedback=feedback,
        mix=mix
    )

    ir_signal = pp_delay.create_pingpong_ir(samplerate, duration_seconds=duration_sec_plot)
    num_samples_plot = len(ir_signal)

    print(f"Generazione IR Ping Pong Delay sincronizzato a {BPM} BPM.")
    print(f"Ritardi: T_L={delay_time_l}s, T_R={delay_time_r}s. Feedback={feedback}, Mix={mix}")

    time_axis = np.arange(num_samples_plot) / samplerate

    plt.figure(figsize=(14, 6))

    # Canale Sinistro (L)
    plt.subplot(2, 1, 1)
    plt.stem(time_axis, ir_signal[:, 0], linefmt='b-', markerfmt='bo', basefmt="r-")
    plt.title(f"Ping Pong Delay - Canale Sinistro")
    plt.ylabel("Ampiezza L (Normalizzata)")
    plt.grid(True, linestyle='--')
    plt.xlim(-0.1, duration_sec_plot + 0.1)

    # Canale Destro (R)
    plt.subplot(2, 1, 2)
    plt.stem(time_axis, ir_signal[:, 1], linefmt='g-', markerfmt='go', basefmt="r-")
    plt.title(f"Ping Pong Delay - Canale Destro")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Ampiezza R (Normalizzata)")
    plt.grid(True, linestyle='--')
    plt.xlim(-0.1, duration_sec_plot + 0.1)

    plt.suptitle(f"Risposta Impulsiva Sincronizzata (T_L=T_R=0.5s)", fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

    print(f"Grafico IR Ping Pong Delay completato. Ritardi: {delay_time_l}s e {delay_time_r}s.")

    # plt.savefig('ir_ping_pong.png', dpi=300)
    # plt.close()


def ir_cabinet_test():
    file_path = 'C:\\Users\\elede\\PycharmProjects\\PythonProject\\thesis_project\\ir_cabinet\\cenzo_celestion_V30.wav'
    # file_path = 'C:\\Users\\elede\\PycharmProjects\\PythonProject\\thesis_project\\ir_cabinet\\G12T75-4x12.wav'
    # file_path = 'C:\\Users\\elede\\PycharmProjects\\PythonProject\\thesis_project\\ir_cabinet\\V30-4x12.wav'

    ZOOM_TIME_SECONDS = 0.03

    try:
        rate, data = wavfile.read(file_path)
    except FileNotFoundError:
        print(f"ERRORE: File non trovato al percorso: {file_path}")
        exit()
    except Exception as e:
        print(f"Si è verificato un errore durante la lettura del file: {e}")
        exit()

    is_stereo = data.ndim > 1
    num_channels = data.ndim if is_stereo else 1
    print(f"File letto. Canali: {num_channels}. Zoom impostato a {ZOOM_TIME_SECONDS}s.")

    samples_to_plot = data[:, 0] if is_stereo else data

    num_samples = len(samples_to_plot)
    duration = num_samples / rate
    time = np.linspace(0., duration, num_samples)

    plt.figure(figsize=(15, 6))

    if is_stereo:
        # --- Trattazione STEREO ---
        channel_L = data[:, 0]
        channel_R = data[:, 1]

        # Plotta il Canale Sinistro (L)
        plt.plot(time, channel_L, color='#0077b6', linewidth=1, label='Canale Sinistro (Mic 1)')

        # Plotta il Canale Destro (R)
        plt.plot(time, channel_R, color='#d90429', linewidth=1, label='Canale Destro (Mic 2)', alpha=0.7)

        plt.title('Risposta Impulsiva del Cabinet')

    else:
        plt.plot(time, data, color='#ef7600', linewidth=1, label='Canale Mono')

        max_amplitude_index = np.argmax(np.abs(data))
        max_amplitude_time = time[max_amplitude_index]
        plt.axvline(max_amplitude_time, color='k', linestyle='--', linewidth=1, label='Picco Impulso')

        plt.title('Risposta Impulsiva del Cabinet')

    plt.xlabel('Tempo [s]')
    plt.ylabel('Ampiezza')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.xlim(0, ZOOM_TIME_SECONDS)
    plt.legend()
    plt.tight_layout()
    plt.show()

    print(f"\nVisualizzazione completata per il segnale {'STEREO' if is_stereo else 'MONO'}.")

    # plt.savefig('ir_cenzo_celestion_V30.png', dpi=300)
    # plt.savefig('ir_G12T75-4x12.png', dpi=300)
    # plt.savefig('ir_V30-4x12.png', dpi=300)
    # plt.close()


def ir_bessel_test():
    """
    Verifica e visualizza le Risposte all'Impulso (IR) sintetiche generate dai modelli di Bessel.
    Visualizza i grafici in 2x2 con colori specifici e un range di tempo esteso.
    """
    SAMPLERATE = 44100

    # --- Modifica qui: Estendi la durata per vedere il decadimento ---
    IR_DURATION = 0.200  # 200ms (per mostrare meglio il decadimento)

    # Colori specifici per ogni modello
    colors = ['blue', 'red', 'green', 'magenta']

    # Parametri testati (che producono effetti visibili)
    bessel_configs = [
        {'ir_model': 'linear', 'kx': 0.28, 'offset': 0.0, 'alpha': 0.0, 'mix': 1.0},
        {'ir_model': 'quadratic', 'kx': 1.0, 'offset': 0.0, 'alpha': 0.0, 'mix': 1.0},
        {'ir_model': 'offset', 'kx': 0.28, 'offset': 1, 'alpha': 0.0, 'mix': 1.0},
        {'ir_model': 'exp_decay', 'kx': 5.0, 'offset': 0.0, 'alpha': 0.01, 'mix': 1.0},
    ]

    fig, axes = plt.subplots(2, 2, figsize=(15, 10), sharex=False, sharey=False)  # Rimosso sharex/sharey

    # Rendi gli assi un array piatto per l'iterazione
    axes = axes.flatten()

    fig.suptitle('Risposte all\'Impulso Sintetiche (Modelli Bessel)', fontsize=16)

    for i, params in enumerate(bessel_configs):
        model_name = params['ir_model'].capitalize()

        # 1. Istanzia l'effetto Cabinet
        cabinet = CabinetEffect(ir_source='bessel', **params)

        # 2. Estrai l'IR generata
        # Per questa visualizzazione, rigeneriamo l'IR con la durata estesa direttamente,
        # poiché la durata dell'IR in cabinet.py è fissa a 50ms per il processing audio.
        # Questo è solo a scopo di visualizzazione nel test.
        ir = CabinetEffect._generate_bessel_ir(SAMPLERATE,
                                               ir_model=params['ir_model'],
                                               kx=params['kx'],
                                               offset=params['offset'],
                                               alpha=params['alpha'])

        # Se l'IR è più lunga di quanto previsto, la tagliamo per la visualizzazione coerente
        samples_to_plot = int(SAMPLERATE * IR_DURATION)
        if len(ir) > samples_to_plot:
            ir = ir[:samples_to_plot]

        time_axis_samples = np.arange(ir.size)
        time_axis_seconds = time_axis_samples / SAMPLERATE

        # 3. Disegna sull'asse corrente con il colore specifico
        axes[i].plot(time_axis_seconds, ir, linewidth=1.0, color=colors[i])

        # --- Aggiornamento del titolo per coerenza con il grafico precedente ---
        title_str = f"{model_name}: J1({params['kx']}"
        if model_name == 'Quadratic':
            title_str += f" * x²)"
        elif model_name == 'Offset':
            title_str += f" * (x + {params['offset']}))"
        elif model_name == 'Exp_decay':
            title_str += f" * exp(-{params['alpha']} * x))"
        else:  # Linear
            title_str += f" * x)"

        axes[i].set_title(title_str)
        axes[i].set_ylabel("Ampiezza")
        axes[i].grid(True)
        axes[i].set_xlim(0, IR_DURATION)  # Imposta l'estensione dell'asse X

    # Imposta l'etichetta X per tutti i grafici (o solo l'ultima riga se preferisci)
    for ax in axes:  # Etichetta tutti per chiarezza con un layout più ampio
        ax.set_xlabel("Tempo (secondi)")

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

    print(f"Grafico IR Bessel completato.")


def ir_chain_test():
    """
        Genera e grafica la Risposta Impulsiva della catena di effetti:
        Cabinet (cenzo_celestion_v30) -> Delay Mono -> Riverbero.
        """
    SAMPLERATE = 44100
    CABINET_FILE_PATH = 'C:\\Users\\elede\\PycharmProjects\\PythonProject\\thesis_project\\ir_cabinet\\cenzo_celestion_V30.wav'

    # --- 1. Caricamento IR Cabinet (Primo Effetto) ---
    try:
        rate, cabinet_data = wavfile.read(CABINET_FILE_PATH)
        if rate != SAMPLERATE:
            print(f"Attenzione: Samplerate del file IR ({rate} Hz) non corrisponde a quello target ({SAMPLERATE} Hz).")

        # Prendi solo il canale sinistro/mono. Assumiamo che, per la catena, l'IR di partenza sia mono.
        cabinet_ir = cabinet_data[:, 0] if cabinet_data.ndim > 1 else cabinet_data

        # Normalizzazione: assicuriamo che il picco massimo sia 1.0 (o usiamo un fattore di normalizzazione)
        cabinet_ir = cabinet_ir / np.max(np.abs(cabinet_ir))

        # La Risposta Impulsiva della Catena inizia con l'IR del Cabinet
        chain_ir = cabinet_ir

    except FileNotFoundError:
        print(f"ERRORE: File IR Cabinet non trovato al percorso: {CABINET_FILE_PATH}")
        return
    except Exception as e:
        print(f"ERRORE nella lettura del file IR Cabinet: {e}")
        return

    # Parametri Delay Mono (secondo effetto)
    delay_time = 0.5
    feedback = 0.6
    delay_mix = 0.4
    delay_mono = DelayEffect(delay_time, feedback, delay_mix)
    IR_DURATION_SEC=3.0
    delay_ir = delay_mono.create_delay_ir(SAMPLERATE, IR_DURATION_SEC)
    print(f"Configurato Delay: T={delay_time}s, F={feedback}, M={delay_mix}")

    # Parametri Riverbero (terzo effetto)
    T60 = 2.0
    NUM_REFLECTIONS = 1000
    DECAY_RATE = 2.0
    reverb_mix = 0.5
    reverb = ReverbEffect(T60, NUM_REFLECTIONS, DECAY_RATE, reverb_mix)
    reverb_ir = reverb.create_reverb_ir(SAMPLERATE)
    print(f"Configurato Riverbero: T60={T60}s, Riflessioni={NUM_REFLECTIONS}, M={reverb_mix}")

    # --- 2. Applicazione in Cascata (Convoluzione) ---

    # 2.1. Applicazione Delay sull'IR del Cabinet
    # Convoluzione: chain_ir = Cabinet_IR * Delay_IR
    chain_ir = fftconvolve(chain_ir, delay_ir, mode='full')
    print("Convoluzione Cabinet * Delay completata.")

    # 2.2. Applicazione Riverbero
    # Convoluzione: chain_ir = (Cabinet_IR * Delay_IR) * Reverb_IR
    chain_ir = fftconvolve(chain_ir, reverb_ir, mode='full')
    print("Convoluzione (Cabinet * Delay) * Reverb completata.")

    # --- 3. Normalizzazione Finale ---
    # Normalizza l'IR della catena per una visualizzazione ottimale
    max_amplitude = np.max(np.abs(chain_ir))
    if max_amplitude > 0:
        chain_ir = chain_ir / max_amplitude

    # --- 4. Generazione del Grafico ---

    duration_sec = len(chain_ir) / SAMPLERATE
    time_axis = np.arange(len(chain_ir)) / SAMPLERATE

    plt.figure(figsize=(14, 6))

    # Plotta l'IR risultante (potrebbe essere molto lungo, usiamo plot non stem)
    plt.plot(time_axis, chain_ir, linewidth=0.5, color='#3c6e71', label='IR Catena Completa')

    # Dettagli del grafico
    plt.title("Risposta Impulsiva della Catena di Effetti (Cabinet $\\rightarrow$ Delay $\\rightarrow$ Riverbero)")
    plt.xlabel("Tempo (secondi)")
    plt.ylabel("Ampiezza Normalizzata")

    # Limita l'asse X per una migliore visualizzazione
    # La durata totale può essere lunga (Delay * Reverb), la limitiamo a 3 secondi per vedere l'attacco
    # e le prime ripetizioni del delay
    plot_limit_sec = min(duration_sec, 4.5)
    plt.xlim(0, plot_limit_sec)

    plt.grid(True, linestyle=':', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.show()

    print(f"\nGrafico IR Catena completato. Durata totale dell'IR: {duration_sec:.2f} s.")