import numpy as np # type: ignore
import skfuzzy as fuzz # type: ignore
import matplotlib.pyplot as plt # type: ignore

# Definisi variabel input
SUM = np.arange(0, 101, 1)
KA = np.arange(0, 101, 1)

# Definisi variabel output
Decision = np.arange(0, 101, 1)

# Fungsi keanggotaan untuk Skor Ujian Masuk (SUM)
SUM_low = fuzz.trimf(SUM, [0, 0, 50])
SUM_medium = fuzz.trimf(SUM, [30, 50, 70])
SUM_high = fuzz.trimf(SUM, [60, 100, 100])

# Fungsi keanggotaan untuk Ketersediaan Anggaran (KA)
KA_low = fuzz.trimf(KA, [0, 0, 50])
KA_medium = fuzz.trimf(KA, [30, 50, 70])
KA_high = fuzz.trimf(KA, [60, 100, 100])

# Fungsi keanggotaan untuk Keputusan
Decision_not_accepted = fuzz.trimf(Decision, [0, 0, 50])
Decision_considered = fuzz.trimf(Decision, [30, 50, 70])
Decision_accepted = fuzz.trimf(Decision, [60, 100, 100])

# Visualisasi fungsi keanggotaan
fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, figsize=(10, 15))

ax0.plot(SUM, SUM_low, 'b', label='Low')
ax0.plot(SUM, SUM_medium, 'g', label='Medium')
ax0.plot(SUM, SUM_high, 'r', label='High')
ax0.set_title('Skor Ujian Masuk')
ax0.legend()

ax1.plot(KA, KA_low, 'b', label='Low')
ax1.plot(KA, KA_medium, 'g', label='Medium')
ax1.plot(KA, KA_high, 'r', label='High')
ax1.set_title('Ketersediaan Anggaran')
ax1.legend()

ax2.plot(Decision, Decision_not_accepted, 'b', label='Tidak Layak Diterima')
ax2.plot(Decision, Decision_considered, 'g', label='Dipertimbangkan')
ax2.plot(Decision, Decision_accepted, 'r', label='Layak Diterima')
ax2.set_title('Keputusan Penerimaan')
ax2.legend()

plt.tight_layout()
plt.show()
