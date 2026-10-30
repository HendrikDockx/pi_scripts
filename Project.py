import os
import time
import requests
import cv2
import face_recognition
import digitalio

import board
import busio
import adafruit_ssd1306
import paho.mqtt.client as mqtt


from PIL import Image
from PIL import ImageDraw

# =====================================
# VARIABLES Pico
# =====================================

distance = 999
lux = 0
visitor_detected = False

# =====================================
# THINGSPEAK
# =====================================

API_KEY = "E7LQD6RKKMTMCEYV"



# =====================================
# OLED SPI
# =====================================

spi = busio.SPI(
    clock=board.SCK,
    MOSI=board.MOSI
)

dc = digitalio.DigitalInOut(board.D6)
reset = digitalio.DigitalInOut(board.D4)
oled_cs = digitalio.DigitalInOut(board.D5)

oled = adafruit_ssd1306.SSD1306_SPI(
    128,
    64,
    spi,
    dc,
    reset,
    oled_cs
)

image = Image.new("1", (128, 64))
draw = ImageDraw.Draw(image)

# =====================================
# OLED FUNCTIONS
# =====================================

def oled_text(text):

    draw.rectangle((0,0,128,64), fill=0)

    draw.text((0,20), text, fill=255)

    oled.image(image)
    oled.show()
    
# =====================================
# RGB LED FUNCTIONS
# =====================================
    
    
def rgb_red():

    mqtt_client.publish(
        "deurbel/status",
        "RED"
    )

def rgb_green():

    mqtt_client.publish(
        "deurbel/status",
        "GREEN"
    )

def rgb_blue():

    mqtt_client.publish(
        "deurbel/status",
        "BLUE"
    )

def rgb_off():

    mqtt_client.publish(
        "deurbel/status",
        "OFF"
    )
    
def cleanup():

    try:

        rgb_off()

        oled_text("Gestopt")

        mqtt_client.publish(
            "deurbel/motor",
            "STOP"
        )

        mqtt_client.loop_stop()

        camera.release()

    except Exception as e:

        print("Cleanup fout:", e)
        
        
# =====================================
# Stepper motor
# =====================================

def open_door():

    mqtt_client.publish(
        "deurbel/motor",
        "OPEN"
    )

# =====================================
# FACE DATABASE
# =====================================

known_encodings = []
known_names = []

for file in os.listdir("pi_scripts/bekende_gezichten"):

    path = os.path.join(
        "pi_scripts/bekende_gezichten",
        file
    )

    try:

        img = face_recognition.load_image_file(
            path
        )

        encodings = face_recognition.face_encodings(
            img
        )

        if len(encodings) > 0:

            known_encodings.append(
                encodings[0]
            )

            known_names.append(
                os.path.splitext(file)[0]
            )

            print(
                f"Loaded: {file}"
            )

    except Exception as e:

        print(
            f"Fout in {file}: {e}"
        )

print("Gezichten geladen")

# =====================================
# CAMERA
# =====================================

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Kan camera niet openen")
    exit()

# =====================================
# THINGSPEAK
# =====================================

def send_to_thingspeak(
    distance,
    person,
    authorized
):

    requests.get(
        "https://api.thingspeak.com/update",
        params={
            "api_key": "E7LQD6RKKMTMCEYV",
            "field1": distance,
            "status": person,
            "field2": int(authorized)
        },
        timeout=5
    )
    
# =====================================
# MQTT
# =====================================    

def on_message(
    client,
    userdata,
    msg
):

    global distance
    global lux

    payload = msg.payload.decode()

    if msg.topic == "deurbel/distance":

        distance = float(payload)

        print (
            f"Afstand: {distance:.1f} cm"
        )

    elif msg.topic == "deurbel/light":

        lux = float(payload)

        print(
            f"Lux: {lux:.1f}"
        )   


# =====================================
# MQTT CLIENT
# =====================================


mqtt_client = mqtt.Client()

mqtt_client.on_message = on_message

mqtt_client.connect(
    "broker.hivemq.com",
    1883,
    60
)

mqtt_client.subscribe(
    "deurbel/distance"
)

mqtt_client.subscribe(
    "deurbel/light"
)

mqtt_client.subscribe(
    "deurbel/motor_feedback"
)

mqtt_client.loop_start()

# =====================================
# STARTUP
# =====================================


rgb_blue()

oled_text("Deurbel actief")

print(
    "Wachten op MQTT berichten..."
)

# =====================================
# Main Loop
# =====================================


while True:

    try:

        if distance < 50 and not visitor_detected:

            visitor_detected = True

            print(
                f"Bezoeker op {distance:.1f} cm"
            )

            rgb_blue()

            oled_text(
                f"Bezoeker\nLux:{int(lux)}"
            )

            ret, frame = camera.read()

            if not ret:

                print("Camera fout")

                visitor_detected = False
                continue

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            encodings = (
                face_recognition.face_encodings(
                    rgb
                )
            )

            authorized = False
            person_name = "Unknown"

            for face_encoding in encodings:

                matches = (
                    face_recognition.compare_faces(
                        known_encodings,
                        face_encoding,
                        tolerance=0.5
                    )
                )

                if True in matches:

                    idx = matches.index(True)

                    person_name = (
                        known_names[idx]
                    )

                    authorized = True

                    break

            if authorized:

                message = (
                    f"Welkom {person_name}"
                )

                rgb_green()
                
                open_door()

            else:

                message = (
                    "Onbekende bezoeker"
                )

                rgb_red()

            print(message)

            oled_text(
                f"{message}\nLux:{int(lux)}"
            )

            send_to_thingspeak(
                distance,
                person_name,
                authorized
            )

            os.makedirs(
                "visitors",
                exist_ok=True
            )

            filename = (
                f"visitors/{int(time.time())}.jpg"
            )

            cv2.imwrite(
                filename,
                frame
            )

            print(
                f"Foto opgeslagen: {filename}"
            )
            
            time.sleep(5)
            

        # reset wanneer bezoeker weg is
        if distance > 70:

            visitor_detected = False

            oled_text(
                f"Deurbel actief\nLux:{int(lux)}"
            )

            rgb_blue()

        time.sleep(0.2)

    except KeyboardInterrupt:

        print(
            "Programma gestopt"
        )
        
        cleanup()

        break

    except Exception as e:

        print(
            "Fout:",
            e
        )
        
        cleanup()

        time.sleep(1)