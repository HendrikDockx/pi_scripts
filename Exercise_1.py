import time
import board
import digitalio

print("infinite flashlight")

led = digitalio.DigitalInOut(board.D17)
led.direction = digitalio.Direction.OUTPUT

while True:
    led.value = True
