import time
import board
import wifi
import socketpool
import busio
import digitalio

import adafruit_hcsr04
import adafruit_bh1750

from adafruit_minimqtt.adafruit_minimqtt import MQTT

# =====================================
# WIFI
# =====================================

wifi.radio.connect(
    "SSID",
    "PWD"
)

print("Wifi verbonden")

pool = socketpool.SocketPool(
    wifi.radio
)

# =====================================
# RGB LED
# =====================================

red = digitalio.DigitalInOut(board.GP16)
green = digitalio.DigitalInOut(board.GP17)
blue = digitalio.DigitalInOut(board.GP18)

for led in [red, green, blue]:
    led.direction = digitalio.Direction.OUTPUT


def rgb_off():

    red.value = False
    green.value = False
    blue.value = False


def rgb_red():

    red.value = True
    green.value = False
    blue.value = False


def rgb_green():

    red.value = False
    green.value = True
    blue.value = False


def rgb_blue():

    red.value = False
    green.value = False
    blue.value = True


# =====================================
# STEPPERMOTOR
# =====================================

in1 = digitalio.DigitalInOut(board.GP2)
in2 = digitalio.DigitalInOut(board.GP3)
in3 = digitalio.DigitalInOut(board.GP4)
in4 = digitalio.DigitalInOut(board.GP5)

for pin in [in1, in2, in3, in4]:
    pin.direction = digitalio.Direction.OUTPUT

sequence = [
    [1,0,0,0],
    [1,1,0,0],
    [0,1,0,0],
    [0,1,1,0],
    [0,0,1,0],
    [0,0,1,1],
    [0,0,0,1],
    [1,0,0,1]
]


def set_step(step):

    in1.value = step[0]
    in2.value = step[1]
    in3.value = step[2]
    in4.value = step[3]


def motor_off():

    in1.value = False
    in2.value = False
    in3.value = False
    in4.value = False


def step_motor(steps, direction=1):

    for _ in range(steps):

        if direction == 1:
            seq = sequence
        else:
            seq = reversed(sequence)

        for step in seq:

            set_step(step)

            time.sleep(0.002)

    motor_off()


def open_door():

    print("DEUR OPENEN")

    # ongeveer 90 graden

    step_motor(
        512,
        direction=1
    )

    time.sleep(5)

    print("DEUR SLUITEN")

    step_motor(
        512,
        direction=-1
    )

    motor_off()


# =====================================
# HC-SR04
# =====================================

sonar = adafruit_hcsr04.HCSR04(
    trigger_pin=board.GP15,
    echo_pin=board.GP14
)

# =====================================
# BH1750
# =====================================

i2c = busio.I2C(
    board.GP1,
    board.GP0
)

light_sensor = adafruit_bh1750.BH1750(i2c)

# =====================================
# MQTT CALLBACK
# =====================================

def mqtt_message(
    client,
    topic,
    payload
):

    print(
        f"RX -> {topic}: {payload}"
    )

    if topic == "deurbel/status":

        if payload == "RED":
            rgb_red()

        elif payload == "GREEN":
            rgb_green()

        elif payload == "BLUE":
            rgb_blue()

        elif payload == "OFF":
            rgb_off()

    elif topic == "deurbel/motor":

        if payload == "OPEN":

            open_door()


# =====================================
# MQTT CLIENT
# =====================================

mqtt = MQTT(
    broker="broker.hivemq.com",
    socket_pool=pool
)

mqtt.on_message = mqtt_message

mqtt.connect()

mqtt.subscribe(
    "deurbel/status"
)

mqtt.subscribe(
    "deurbel/motor"
)

print("MQTT verbonden")

# =====================================
# STARTUP
# =====================================

rgb_blue()

last_publish = 0

# =====================================
# HOOFDLUS
# =====================================

while True:

    try:

        mqtt.loop()

        if time.monotonic() - last_publish > 2:

            try:

                distance = sonar.distance

                mqtt.publish(
                    "deurbel/distance",
                    f"{distance:.1f}"
                )

                lux = light_sensor.lux

                mqtt.publish(
                    "deurbel/light",
                    f"{lux:.1f}"
                )

                print(
                    f"Afstand: {distance:.1f} cm | Lux: {lux:.1f}"
                )

            except RuntimeError:
                pass

            last_publish = time.monotonic()

        time.sleep(0.1)

    except Exception as e:

        print("Fout:", e)

        time.sleep(1)

