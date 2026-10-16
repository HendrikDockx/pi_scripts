from gpiozero import LED, Button
from time import sleep

led = LED(4)
button = Button(17, pull_up=True)

while True:
    if button.is_pressed:
        led.on()
    else:
        led.off()

    sleep(0.2)