import time
import board
import wifi
import socketpool
import busio
import digitalio

import adafruit_hcsr04
import adafruit_bh1750

from adafruit_minimqtt.adafruit_minimqtt import MQTT

# WIFI

wifi.radio.connect(
    "Telenet-9495",
    "Hollebollebobby27!"
)

pool = socketpool.SocketPool(
    wifi.radio
)

# RGB

red = digitalio.DigitalInOut(board.GP16)
green = digitalio.DigitalInOut(board.GP17)
blue = digitalio.DigitalInOut(board.GP18)

for led in [red, green, blue]:
    led.direction = digitalio.Direction.OUTPUT

# HC-SR04

sonar = adafruit_hcsr04.HCSR04(
    trigger_pin=board.GP15,
    echo_pin=board.GP14
)

# BH1750

i2c = busio.I2C(
    board.GP1,
    board.GP0
)

light = adafruit_bh1750.BH1750(i2c)

# MQTT callback

def message(client, topic, payload):

    print(topic, payload)

    red.value = False
    green.value = False
    blue.value = False

    if payload == "RED":
        red.value = True

    elif payload == "GREEN":
        green.value = True

    elif payload == "BLUE":
        blue.value = True

    elif payload == "OFF":
        red.value = False
        green.value = False
        blue.value = False

mqtt = MQTT(
    broker="broker.hivemq.com",
    socket_pool=pool
)

mqtt.on_message = message

mqtt.connect()

mqtt.subscribe(
    "deurbel/status"
)

print("MQTT OK")

last_publish = 0

while True:

    mqtt.loop()

    if time.monotonic() - last_publish > 2:

        try:

            distance = sonar.distance

            mqtt.publish(
                "deurbel/distance",
                str(distance)
            )

            mqtt.publish(
                "deurbel/light",
                str(light.lux)
            )

        except RuntimeError:
            pass

        last_publish = time.monotonic()
