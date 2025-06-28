import adafruit_dht
import board
import RPi.GPIO as GPIO
import time

# Pin Setup
DHT_PIN = board.D4  # DHT sensor pin
RELAY_AC = 17
RELAY_TV = 27
RELAY_LAMP = 22
PIR_PIN = 23

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_AC, GPIO.OUT)
GPIO.setup(RELAY_TV, GPIO.OUT)
GPIO.setup(RELAY_LAMP, GPIO.OUT)
GPIO.setup(PIR_PIN, GPIO.IN)

# Inisialisasi sensor DHT
dht = adafruit_dht.DHT22(DHT_PIN)

# Baca sensor dan kontrol perangkat
try:
    suhu = dht.temperature
    kelembaban = dht.humidity
    penghuni = GPIO.input(PIR_PIN)
    
    # Simulasi logika
    if suhu > 30 and penghuni:
        GPIO.output(RELAY_AC, GPIO.HIGH)
    else:
        GPIO.output(RELAY_AC, GPIO.LOW)

    if penghuni:
        GPIO.output(RELAY_TV, GPIO.HIGH)
        GPIO.output(RELAY_LAMP, GPIO.HIGH)
    else:
        GPIO.output(RELAY_TV, GPIO.LOW)
        GPIO.output(RELAY_LAMP, GPIO.LOW)

    print(f\"Suhu: {suhu} C, Kelembaban: {kelembaban} %, Penghuni: {penghuni}\")

except RuntimeError as e:
    print(\"Error baca sensor:\", e)

finally:
    dht.exit()
    GPIO.cleanup()
