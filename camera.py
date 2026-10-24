import board
import digitalio
import time

red = digitalio.DigitalInOut(board.GP16)
green = digitalio.DigitalInOut(board.GP17)
blue = digitalio.DigitalInOut(board.GP18)

for led in [red, green, blue]:
    led.direction = digitalio.Direction.OUTPUT

while True:

    red.value = True
    time.sleep(1)
    red.value = False

    green.value = True
    time.sleep(1)
    green.value = False

    blue.value = True
    time.sleep(1)
    blue.value = False