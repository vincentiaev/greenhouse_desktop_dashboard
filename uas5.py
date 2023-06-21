from time import sleep
import paho.mqtt.client as mqtt
import sys
# from PyQt6.QtWidgets import (
#     QApplication, QWidget
# )
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
from datetime import datetime

topicpub_temp = "4170/dht11/temp"
topicpub_hum = "4170/dht11/hum"
topicpub_soil = "4170/soil"
topicpub_ldr = "4170/ldr"
topicpub_flow = "4170/flow"

broker = "192.168.41.70"
client = mqtt.Client("mkiuygfdserthjk")

temperature_data = deque(maxlen=5)
humidity_data = deque(maxlen=5)
soil_data = deque(maxlen=5)
ldr_data = deque(maxlen=5)
flow_data = deque(maxlen=5)
current_times = deque(maxlen=5)

plt.rcParams['toolbar'] = 'None'

fig, ((axflow, axLDR), (axDHT, axSoil), (axDHTgauge, axSoilGauge)) = plt.subplots(3, 2, figsize=(16, 10))
plt.subplots_adjust(top=0.923,
                    bottom=0.058,
                    left=0.11,
                    right=0.978,
                    hspace=0.487,
                    wspace=0.2)

fig.suptitle('GREENHOUSE', fontsize=18)


def get_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_times.append(current_time)
    print(current_times)

def update_soil():
    axSoil.clear()
    axSoil.plot(current_times, soil_data, "ro-")
    axSoil.set_xlabel('Time')
    axSoil.set_ylabel('Soil Moisture')
    axSoil.set_title('Soil Sensor Data')
    plt.pause(0.1)

def update_LDR():
    axLDR.clear()
    axLDR.plot(current_times, ldr_data, "bo-")
    axLDR.set_xlabel('Time')
    axLDR.set_ylabel('Lux')
    axLDR.set_title('LDR Sensor Data')
    plt.pause(0.1)

def update_DHT():
    if len(temperature_data) == len(humidity_data):
        axDHT.clear()
        axDHT.plot(current_times, temperature_data, "mo-" ,label="Temperature")
        axDHT.plot(current_times, humidity_data, "co-" ,label="Humidity")
        axDHT.set_xlabel('Time')
        axDHT.set_ylabel('Temperature / Humidity')
        axDHT.set_title('DHT Sensor Data')
        axDHT.legend()
    else:
        axDHT.text(0.5, 0.5, 'Data dimension mismatch', ha='center', va='center')
    plt.pause(0.1)

def update_flow():
    axflow.clear()
    axflow.plot(current_times, flow_data, "yo-")
    axflow.set_xlabel('Time')
    axflow.set_ylabel('ml/s')
    axflow.set_title('Flow Sensor Data')
    plt.pause(0.1)

def update_dht_gauge():
    axDHTgauge.clear() 
    axDHTgauge.set_title('Temperature Sensor')
    axDHTgauge.set_xlim(0, 50)  
    axDHTgauge.set_ylim(0, 1)  
    axDHTgauge.set_xticks([])
    axDHTgauge.set_yticks([])
    
    value = temperature_data[-1] if temperature_data else 0
    axDHTgauge.barh(0, value, 5, align='center', color='#bfc8e0')
    axDHTgauge.text(value / 2, 0.5, str(value), fontsize='14', ha='center', va='center')
    
def update_soil_gauge():
    axSoilGauge.clear()
    axSoilGauge.set_title('Soil Moisture Sensor')
    axSoilGauge.set_xlim(0, 100)
    axSoilGauge.set_ylim(0, 1)
    axSoilGauge.set_xticks([])
    axSoilGauge.set_yticks([])
    
    value = soil_data[-1] if soil_data else 0
    axSoilGauge.barh(0, value, 5, align='center', color='#b88777')
    axSoilGauge.text(value / 2, 0.5, str(value), fontsize='14', ha='center', va='center')

def on_message(client, userdata, message):
    data = float(message.payload.decode("utf-8"))
            
    if message.topic == topicpub_temp:
        get_time()
        temperature_data.append(data)
        # print(temperature_data)
        update_DHT()
        update_dht_gauge()
               
    elif message.topic == topicpub_hum:
        humidity_data.append(data)
        update_DHT()

    elif message.topic == topicpub_soil:
        soil_data.append(data)
        # print(soil_data)
        update_soil()
        update_soil_gauge()
         
    elif message.topic == topicpub_ldr:
        ldr_data.append(data)
        # print(ldr_data)
        update_LDR()
                                        
    elif message.topic == topicpub_flow:
        flow_data.append(data)
        # print(flow_data)
        update_flow()

client.connect(broker)
client.subscribe(topicpub_temp)
client.subscribe(topicpub_hum)
client.subscribe(topicpub_soil)
client.subscribe(topicpub_ldr)
client.subscribe(topicpub_flow)

client.on_message = on_message
sleep(2)
client.loop_forever()

bar = axDHTgauge.barh(0, 0, align='center')
bar2 = axSoilGauge.barh(0, 0, align='center')  

plt.ion() 

while True:
    try:
        plt.pause(0.1)
    except KeyboardInterrupt:
        break

plt.show()
