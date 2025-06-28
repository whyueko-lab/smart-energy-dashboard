import time
import random
from datetime import datetime

# Simulasi pembacaan sensor DHT dan PIR
def baca_sensor_simulasi():
    suhu = random.uniform(20, 35)  # Suhu acak
    kelembaban = random.uniform(40, 80)  # Kelembaban acak
    penghuni = random.choice([True, False])  # Simulasi PIR
    return kelembaban, suhu, penghuni

# Fungsi kontrol virtual
def kontrol_ac(suhu, penghuni):
    if suhu > 30 and penghuni:
        print("✅ AC DINYALAKAN")
    elif suhu < 25:
        print("❌ AC DIMATIKAN")

def kontrol_tv(penghuni, jam):
    if penghuni and 18 <= jam <= 22:
        print("✅ TV DINYALAKAN")
    else:
        print("❌ TV DIMATIKAN")

def kontrol_lampu(penghuni, jam):
    if penghuni and (jam >= 18 or jam < 6):
        print("✅ LAMPU DINYALAKAN")
    else:
        print("❌ LAMPU DIMATIKAN")

# Loop simulasi
try:
    while True:
        kelembaban, suhu, penghuni_ada = baca_sensor_simulasi()
        now = datetime.now()
        jam = now.hour

        print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}]")
        print(f"Suhu       : {suhu:.1f}°C")
        print(f"Kelembaban : {kelembaban:.1f}%")
        print(f"Penghuni   : {'YA' if penghuni_ada else 'TIDAK'}")

        kontrol_ac(suhu, penghuni_ada)
        kontrol_tv(penghuni_ada, jam)
        kontrol_lampu(penghuni_ada, jam)

        time.sleep(5)

except KeyboardInterrupt:
    print("\nSimulasi dihentikan.")
