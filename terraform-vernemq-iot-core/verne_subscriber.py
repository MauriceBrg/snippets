import paho.mqtt.client as mqtt

import verne_config

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    print("Subscribing to", verne_config.VERNE_TOPIC)
    client.subscribe(verne_config.VERNE_TOPIC)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def main():

    client = mqtt.Client()
    client.username_pw_set(verne_config.VERNE_USERNAME, verne_config.VERNE_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(verne_config.VERNE_HOST, verne_config.VERNE_PORT, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()

if __name__ == "__main__":
    main()