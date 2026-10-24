import lgpio as GPIO 
import time 

TRIG = 23
ECHO = 24

h=GPIO.gpiochip_open(0)
GPIO.gpio_claim_input(h, ECHO)
GPIO.gpio_claim_output(h, TRIG,)

def get_distance():
    GPIO.gpio_write(h, TRIG, 0)
    time.sleep(0.000002)
    GPIO.gpio_write(h, TRIG, 1)
    time.sleep(0.00001)
    GPIO.gpio_write(h, TRIG, 0)

    while GPIO.gpio_read(h, ECHO) == 0:
        pulse_start = time.time()

    while GPIO.gpio_read(h, ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = round(pulse_duration * 17150, 2)
    return distance

if __name__ == "__main__":
    try:
        while True:
            dist = get_distance()
            print(f"Distance: {dist} cm")
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.gpiochip_close(h)
        print("Exiting...")