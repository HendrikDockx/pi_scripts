import board
import digitalio
import time
import threading
from pathlib import Path

from pathlib import Path

PWM_ROOT = Path("/sys/class/pwm/pwmchip0")
PWM_CHANNEL = 0
PWM_DIR = PWM_ROOT / f"pwm{PWM_CHANNEL}"
PWM_PERIOD_NS = 1_000_000  # 1 kHz

def set_led_brightness(value):
    duty_ns = PWM_PERIOD_NS * value // 65535
    (PWM_DIR / "duty_cycle").write_text(str(duty_ns))

# Export the hardware PWM channel for userspace control.
if PWM_DIR.exists():
    raise RuntimeError(
        f"{PWM_DIR} is already exported; check whether another program is using it"
    )

(PWM_ROOT / "export").write_text(str(PWM_CHANNEL))
(PWM_DIR / "period").write_text(str(PWM_PERIOD_NS))
set_led_brightness(duty_cycle_16bit)
(PWM_DIR / "enable").write_text("1")

def setup_switch(pin):
    sw = digitalio.DigitalInOut(pin)
    sw.direction = digitalio.Direction.INPUT
    sw.pull = digitalio.Pull.UP
    return sw

sw0 = setup_switch(SW0_PIN)
sw1 = setup_switch(SW1_PIN)

# --- Thread Tasks ---

def task_input():
    """Handles button presses to update the global duty cycle."""
    global duty_cycle_16bit
    print("Input thread started.")
    while not exit_event.is_set():
        # Increase Brightness
        if not sw0.value: 
            time.sleep(DEBOUNCE)
            duty_cycle_16bit = min(65535, duty_cycle_16bit + 6554)
            print(f"Update: {round((duty_cycle_16bit/65535)*100)}%")

         # Decrease Brightness
        if not sw1.value:
            time.sleep(DEBOUNCE)
            duty_cycle_16bit = max(0, duty_cycle_16bit - 6554)
            print(f"Update: {round((duty_cycle_16bit/65535)*100)}%")
        time.sleep(0.01)

def task_pwm_update():
    """Periodically pushes the global duty cycle value to the hardware."""
    print("PWM thread started.")
    while not exit_event.is_set():
        set_led_brightness(duty_cycle_16bit)
        time.sleep(0.1)
        
# --- Main Execution ---

# Initialize Threads
t1 = threading.Thread(target=task_input, daemon=True)
t2 = threading.Thread(target=task_pwm_update, daemon=True)

print("Starting threads...")
t1.start()
t2.start()

try:
    counter = 0
    while True:
        # Main thread is now free for other logic
        print(f"Main thread heart beat: {counter}")
        counter += 1
        time.sleep(2)
except KeyboardInterrupt:
    print("\nStopping...")
    exit_event.set() # Signal threads to stop
    t1.join() # Wait for thread to finish
    t2.join() # Wait for thread to finish

finally:
    set_led_brightness(0)
    (PWM_DIR / "enable").write_text("0")
    (PWM_ROOT / "unexport").write_text(str(PWM_CHANNEL))
    print("Done.")


