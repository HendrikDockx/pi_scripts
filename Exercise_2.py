import time
import board
import digitalio

print("All of the lights!")

leds = []

for pin in [board.D17, board.D27, board.D22, board.D23]:
    led = digitalio.DigitalInOut(pin)
    led.direction = digitalio.Direction.OUTPUT
    leds.append(led)
        
    

while True:
    for led in (leds):
        led.value = True
        
        time.sleep(0.5)
        
    for led in (leds):
        led.value = False
        
        time.sleep(0.5)    
