import network
import urequests
import utime
import dht
import machine

# Konfigurasi WiFi
SSID = "Redmi"
PASSWORD = "rangga12"

# Konfigurasi Ubidots
UBIDOTS_TOKEN = "BBUS-HNFUlAWy6fMbCtK9227wyKK1PfgY2t"
DEVICE_LABEL = "esp32"
VARIABLE_TEMP = "temperature"
VARIABLE_HUMID = "humidity"
VARIABLE_PIR = "motion"
UBIDOTS_URL = "http://industrial.api.ubidots.com/api/v1.6/devices/" + DEVICE_LABEL

# Konfigurasi Flask
FLASK_URL = "http://192.168.43.88:6500/sensor"  # Ganti dengan IP laptop Anda

# Inisialisasi koneksi WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    timeout = 10  # Waktu tunggu maksimum dalam detik

    while not wlan.isconnected() and timeout > 0:
        print("Menghubungkan ke WiFi...")
        utime.sleep(1)
        timeout -= 1

    if wlan.isconnected():
        print("Terhubung ke WiFi", wlan.ifconfig())
    else:
        print("Gagal terhubung ke WiFi. Reboot ESP32...")
        machine.reset()  # Reboot otomatis jika WiFi gagal

# Inisialisasi sensor dan LED
sensor_dht = dht.DHT11(machine.Pin(4))  # DHT11 di GPIO 4
pir_sensor = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_DOWN)  # PIR di GPIO 2 dengan pull-down resistor
led = machine.Pin(15, machine.Pin.OUT)  # LED di GPIO 15

def send_to_ubidots(temp, hum, motion):
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": UBIDOTS_TOKEN
    }
    data = {
        VARIABLE_TEMP: {"value": temp},
        VARIABLE_HUMID: {"value": hum},
        VARIABLE_PIR: {"value": motion}
    }
    print("Mengirim data ke Ubidots...")
    try:
        response = urequests.post(UBIDOTS_URL, json=data, headers=headers, timeout=5)
        print("Response:", response.text)
        response.close()
    except Exception as e:
        print("Gagal mengirim data ke Ubidots:", e)

def send_to_flask(temp, hum, motion):
    headers = {"Content-Type": "application/json"}
    data = {
        "temperature": temp,
        "humidity": hum,
        "motion": motion
    }
    try:
        response = urequests.post(FLASK_URL, json=data, headers=headers, timeout=5)
        print("Response from Flask:", response.text)
        response.close()
    except Exception as e:
        print("Gagal mengirim data ke Flask:", e)

# Fungsi callback untuk timer
def sensor_callback(t):
    try:
        sensor_dht.measure()
        temp = sensor_dht.temperature()
        hum = sensor_dht.humidity()
        motion = pir_sensor.value()

        # Kontrol LED berdasarkan gerakan PIR
        if motion:
            led.on()  # Nyalakan LED jika ada gerakan
        else:
            led.off()  # Matikan LED jika tidak ada gerakan

        print(f"Suhu: {temp}C, Kelembaban: {hum}%, Gerakan: {motion}")
        send_to_ubidots(temp, hum, motion)
        send_to_flask(temp, hum, motion)  # Mengirim data ke Flask
    except Exception as e:
        print("Error:", e)

# Mulai program
connect_wifi()
timer = machine.Timer(-1)
timer.init(period=5000, mode=machine.Timer.PERIODIC, callback=sensor_callback)
