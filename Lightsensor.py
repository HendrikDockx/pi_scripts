import time
import board
import busio
import paho.mqtt.client as mqtt
from gpiozero import LED

# GPIO pins
led_a = LED(17)   # Above threshold
led_b = LED(27)   # Below threshold

THRESHOLD = 150

# MQTT
BROKER = "localhost"
TOPIC_LUX = "sensors/light"
TOPIC_STATUS = "sensors/light/status"

client = mqtt.Client()
client.connect(BROKER, 1883, 60)

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

            client.publish(
                TOPIC_STATUS,
                "LED_A_ON LED_B_OFF"
            )

        else:
            led_a.off()
            led_b.on()

            client.publish(
                TOPIC_STATUS,
                "LED_A_OFF LED_B_ON"
            )

        time.sleep(1)

except KeyboardInterrupt:
    print("Stopped")

finally:
    led_a.off()
    led_b.off()
    client.disconnect()