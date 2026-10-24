import time
import board
import busio
import paho.mqtt.client as mqtt
import requests
from gpiozero import LED

# GPIO pins
led_a = LED(17)   # Above threshold
led_b = LED(27)   # Below threshold

THRESHOLD = 150

# MQTT
BROKER = "localhost"
TOPIC_LUX = "sensors/light"
TOPIC_STATUS = "sensors/light/status"

# ThingSpeak
THINGSPEAK_API_KEY = "ZX6HZ4UTT30E689J"
THINGSPEAK_URL = "https://api.thingspeak.com/update"

# MQTT client
client = mqtt.Client()
client.connect(BROKER, 1883, 60)

# I2C setup for BH1750
scl_pin = board.D3
sda_pin = board.D2

i2c = busio.I2C(scl_pin, sda_pin)

ADDRESS = 0x23
COMMAND_HIGH_RES = bytearray([0x10])


def get_value():
    result = bytearray(2)

    i2c.writeto_then_readfrom(
        ADDRESS,
        COMMAND_HIGH_RES,
        result
    )

    lux = ((result[0] << 8) | result[1]) / 1.2

    return lux


def send_to_thingspeak(lux, led_a_status, led_b_status):

    payload = {
        "api_key": THINGSPEAK_API_KEY,
        "field1": round(lux, 1),
        "field2": led_a_status,
        "field3": led_b_status
    }

    try:
        response = requests.post(
            THINGSPEAK_URL,
            data=payload,
            timeout=5
        )

        if response.status_code == 200:
            print("ThingSpeak update succesvol")
        else:
            print(f"ThingSpeak fout: {response.status_code}")

    except Exception as e:
        print(f"ThingSpeak verbinding mislukt: {e}")


print("Starting BH1750 + LEDs + MQTT")

try:

    while True:

        lux = get_value()

        print(f"Light: {lux:.1f} lux")

        # MQTT publish lux value
        client.publish(TOPIC_LUX, f"{lux:.1f}")

        if lux > THRESHOLD:

            led_a.on()
            led_b.off()

            led_a_status = 1
            led_b_status = 0

            client.publish(
                TOPIC_STATUS,
                "LED_A_ON LED_B_OFF"
            )

        else:

            led_a.off()
            led_b.on()

            led_a_status = 0
            led_b_status = 1

            client.publish(
                TOPIC_STATUS,
                "LED_A_OFF LED_B_ON"
            )

        # Send data to ThingSpeak
        send_to_thingspeak(
            lux,
            led_a_status,
            led_b_status
        )

        # ThingSpeak minimum update interval
        time.sleep(15)

except KeyboardInterrupt:
    print("Stopped")

finally:
    led_a.off()
    led_b.off()
    client.disconnect()