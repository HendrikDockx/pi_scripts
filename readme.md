Project.py is het script


Verbindingen op Raspberry PI 5

3 volt 3 (pin1): naar positieve lijn rechts op breadboard
5volt (pin2): naar positieve lijn links op breadboard
GND (pin6): naar negatieve lijn rechts
GPIO4 (pin7): RES op OLED
SPIMOSI(pin19): SDA op OLED
SPISCLK(pin23): SCL op OLED
GPIO6(pin31): DC op OLED
GPIO16(pin36): naar pin 15 op PICO


Verbinden op PICO WH 2

Pin1: naar SDA BH1750
Pin2: naar SCL BH1750
Pin15: naar GPIO16 Pi
Pin19: naar Echo SDA op HC-SR04
Pin20: naar Trig SCL op HC-SR04
Pin21: naar RGB LED Rood 
Pin22: naar RGB LED Groen
Pin24: naar RGB LED Blauw 
Pin36: naar 3 volt op BH1750
Pin 38 (GND): naar negatieve lijn links 
Pin40: naar VCC op HC-SR04

Check imports + powerpoints voor vereiste modules


check foto's in git voor info over hardware