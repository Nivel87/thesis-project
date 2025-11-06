import numpy as np
import matplotlib.pyplot as plt
from scipy.special import j1

def bessel_direttivita():
    # Parametri
    c = 343.0
    a = 0.1525
    frequenze = [500, 2000, 5000]
    theta = np.linspace(0, np.pi/2, 500)

    plt.figure(figsize=(8, 5))
    for f in frequenze:
        k = 2 * np.pi * f / c
        x = k * a * np.sin(theta)
        D = np.empty_like(x)
        # Calcola normalmente dove x ≠ 0
        mask = x != 0
        D[mask] = 2 * j1(x[mask]) / x[mask]
        # Imposta manualmente il valore limite
        D[~mask] = 1.0
        D_norm = np.abs(D / D[0])
        plt.plot(np.degrees(theta), D_norm, label=f'{f} Hz')

    plt.title('Direttività di un altoparlante da 12" (funzione di Bessel)')
    plt.xlabel('Angolo θ (gradi)')
    plt.ylabel('|D(θ)| (ampiezza normalizzata)')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(title='Frequenza')
    plt.tight_layout()
    plt.show()
