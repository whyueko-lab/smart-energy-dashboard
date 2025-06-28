import Adafruit_DHT
import RPi.GPIO as GPIO
import time
from datetime import datetime
import random

def baca_sensor_simulasi():
    suhu = random.uniform(20, 35)
    kelembaban = random.uniform(40, 80)
    return kelembaban, suhu


# Setup
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

RELAY_PIN_AC = 17
RELAY_PIN_TV = 27
RELAY_PIN_LAMPU = 22
PIR_SENSOR_PIN = 23  # Pin untuk sensor gerak PIR

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN_AC, GPIO.OUT)
GPIO.setup(RELAY_PIN_TV, GPIO.OUT)
GPIO.setup(RELAY_PIN_LAMPU, GPIO.OUT)
GPIO.setup(PIR_SENSOR_PIN, GPIO.IN)

# Fungsi kendali perangkat
def kontrol_ac(suhu, penghuni):
    if suhu > 30 and penghuni:
        GPIO.output(RELAY_PIN_AC, GPIO.HIGH)
        print("AC DINYALAKAN")
    elif suhu < 25:
        GPIO.output(RELAY_PIN_AC, GPIO.LOW)
        print("AC DIMATIKAN")

def kontrol_tv(penghuni, jam):
    if penghuni and 18 <= jam <= 22:
        GPIO.output(RELAY_PIN_TV, GPIO.HIGH)
        print("TV DINYALAKAN")
    else:
        GPIO.output(RELAY_PIN_TV, GPIO.LOW)
        print("TV DIMATIKAN")

def kontrol_lampu(penghuni, jam):
    if penghuni and (jam >= 18 or jam < 6):  # Malam hari
        GPIO.output(RELAY_PIN_LAMPU, GPIO.HIGH)
        print("LAMPU DINYALAKAN")
    else:
        GPIO.output(RELAY_PIN_LAMPU, GPIO.LOW)
        print("LAMPU DIMATIKAN")

# Loop utama
try:
    while True:
        humidity, temperature = baca_sensor_simulasi()
        penghuni_ada = GPIO.input(PIR_SENSOR_PIN)
        now = datetime.now()
        jam = now.hour

        if temperature:
            print(f"[{now}] Suhu: {temperature:.1f}°C, Penghuni: {'YA' if penghuni_ada else 'TIDAK'}")

            kontrol_ac(temperature, penghuni_ada)
            kontrol_tv(penghuni_ada, jam)
            kontrol_lampu(penghuni_ada, jam)

        time.sleep(10)

except KeyboardInterrupt:
    print("Program dihentikan")
    GPIO.cleanup()
