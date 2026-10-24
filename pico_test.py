import paho.mqtt.client as mqtt

def on_message(
    client,
    userdata,
    msg
):

    afstand = msg.payload.decode()

    print(
        "Bezoeker gedetecteerd:"
    )

    print(
        f"{afstand} cm"
    )

client = mqtt.Client()

client.on_message = on_message

client.connect(
    "broker.hivemq.com",
    1883,
    60
)

client.subscribe(
    "deurbel/bezoeker"
)

client.loop_forever()
