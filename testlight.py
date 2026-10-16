from gpiozero import LED
from time import sleep

led_a = LED(17)
led_b = LED(27)

while True:
    led_a.on()
    led_b.off()
    sleep(1)

    led_a.off()
    led_b.on()
    sleep(1)