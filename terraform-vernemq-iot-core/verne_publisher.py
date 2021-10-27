import json
import random

from datetime import datetime
from time import sleep

import paho.mqtt.client as mqtt
import pytz

import verne_config

def on_publish(client,userdata,result):
    print(f"publish result: {result}")


def main():

    client = mqtt.Client()
    client.username_pw_set(verne_config.VERNE_USERNAME, verne_config.VERNE_PASSWORD)

    client.connect(verne_config.VERNE_HOST, verne_config.VERNE_PORT, 60)

    client.on_publish = on_publish

    while True:
        time = datetime.now(pytz.UTC).isoformat()
        message = {
            "timestamp": time,
            "eventType": random.choice(["FLUX_COMPENSATOR_START", "ENGINE_EXPLODED", "IT_RAINED_FROGS"]),
            "text": f"Hello World!",

        }
        print("Publishing", message, "to", verne_config.VERNE_TOPIC)
        client.publish(verne_config.VERNE_TOPIC, payload=json.dumps(message))
        sleep(5)

if __name__ == "__main__":
    main()