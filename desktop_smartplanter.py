import paho.mqtt.client as mqtt
from collections import deque
from matplotlib import pyplot as plt

mqtt_server = '192.168.1.150'
topic_sub_temp = 'planter/temperature'
topic_sub_hum = 'planter/humidity'
topic_sub_pres = 'planter/pressure'
topic_sub_analog = 'planter/rain'
topic_sub_light = 'planter/light'
topic_sub_soil = 'planter/moisture'

class sensordata:
    def __init__(self, maxdata=1000):
        self.axis_x = deque(maxlen=maxdata)
        self.axis_temp = deque(maxlen=maxdata)
        self.axis_hum = deque(maxlen=maxdata)
        self.axis_pres = deque(maxlen=maxdata)
        self.axis_rain = deque(maxlen=maxdata)
        self.axis_light = deque(maxlen=maxdata)
        self.axis_soil = deque(maxlen=maxdata)

    def add(self, x, temp, hum, pres, rain, light, soil):
        self.axis_x.append(x)
        self.axis_temp.append(temp)
        self.axis_hum.append(hum)
        self.axis_pres.append(pres)
        self.axis_rain.append(rain)
        self.axis_light.append(light)
        self.axis_soil.append(soil)

def main():
    global data, myplot
    data = sensordata()
    print(data)
    fig, axs = plt.subplots(2, 3, figsize=(14, 8))
    fig.suptitle("Smart Planter Sensor Data Plot")
    
    myplot = {
        'soil_moisture': sensorplot(axs[0, 0], "Soil Moisture (%)", 'r'),
        'humidity': sensorplot(axs[0, 1], "Humidity (%)", 'b'),
        'rain': sensorplot(axs[0, 2], "Rain (%)", 'g'),
        'temperature': sensorplot(axs[1, 0], "Temperature (C)", 'm'),
        'light': sensorplot(axs[1, 1], "Light (lux)", 'y'),
        'air_pressure': sensorplot(axs[1, 2], "Air Pressure (hPA)", 'c')
    }

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_server, 1883, 60)
    client.loop_start()

    count = 0
    while True:
        count += 1
        plt.pause(0.25)

class sensorplot:
    def __init__(self, axes, label, color):
        self.axes = axes
        self.lineplot, = axes.plot([], [], label=label, color=color)
        self.axes.set_title(label)
        self.axes.set_xlabel("Time")
        self.axes.set_ylabel(label)
        self.axes.legend()
    def plot(self, x, y):
        self.lineplot.set_data(x, y)
        self.axes.set_xlim(min(x), max(x))
        self.axes.set_ylim(min(y) - 5, max(y) + 5)

def on_connect(client, userdata, flags, reason_code, properties): 
    print("Connected to MQTT Broker, result code = "+str(reason_code))
    client.subscribe(topic_sub_temp)
    client.subscribe(topic_sub_hum)
    client.subscribe(topic_sub_pres)
    client.subscribe(topic_sub_analog)
    client.subscribe(topic_sub_light)
    client.subscribe(topic_sub_soil)
    for plot in myplot.values():
        plot.axes.figure.canvas.draw()

def on_message(client, userdata, msg):
    global data, myplot
    topic = msg.topic
    payload = msg.payload.decode("utf-8")
    try:
        pres = None
        hum = None
        rain = None
        temp = None
        light = None
        soil = None
        if topic == topic_sub_temp:
            temp = float(payload)
        elif topic == topic_sub_hum:
            hum = float(payload)
        elif topic == topic_sub_pres:
            pres = float(payload)
        elif topic == topic_sub_analog:
            rain = float(payload)
        elif topic == topic_sub_light:
            light = float(payload)
        elif topic == topic_sub_soil:
            soil = float(payload)
        else:
            return  # If the topic is not relevant, do nothing

        # Get the current count from the data length
        x = len(data.axis_x)
        
        # Add data to the deque
        if temp is not None:
            data.add(x, temp, data.axis_hum[-1] if data.axis_hum else 0, data.axis_pres[-1] if data.axis_pres else 0, data.axis_rain[-1] if data.axis_rain else 0, data.axis_light[-1] if data.axis_light else 0, data.axis_soil[-1] if data.axis_soil else 0)
        if hum is not None:
            data.add(x, data.axis_temp[-1] if data.axis_temp else 0, hum, data.axis_pres[-1] if data.axis_pres else 0, data.axis_rain[-1] if data.axis_rain else 0, data.axis_light[-1] if data.axis_light else 0, data.axis_soil[-1] if data.axis_soil else 0)
        if pres is not None:
            data.add(x, data.axis_temp[-1] if data.axis_temp else 0, data.axis_hum[-1] if data.axis_hum else 0, pres, data.axis_rain[-1] if data.axis_rain else 0, data.axis_light[-1] if data.axis_light else 0, data.axis_soil[-1] if data.axis_soil else 0)
        if rain is not None:
            data.add(x, data.axis_temp[-1] if data.axis_temp else 0, data.axis_hum[-1] if data.axis_hum else 0, data.axis_pres[-1] if data.axis_pres else 0, rain, data.axis_light[-1] if data.axis_light else 0, data.axis_soil[-1] if data.axis_soil else 0)
        if light is not None:
            data.add(x, data.axis_temp[-1] if data.axis_temp else 0, data.axis_hum[-1] if data.axis_hum else 0, data.axis_pres[-1] if data.axis_pres else 0, data.axis_rain[-1] if data.axis_rain else 0, light, data.axis_soil[-1] if data.axis_soil else 0)
        if soil is not None:
            data.add(x, data.axis_temp[-1] if data.axis_temp else 0, data.axis_hum[-1] if data.axis_hum else 0, data.axis_pres[-1] if data.axis_pres else 0, data.axis_rain[-1] if data.axis_rain else 0, data.axis_light[-1] if data.axis_light else 0, soil)
        myplot['soil_moisture'].plot(data.axis_x, data.axis_soil)
        myplot['humidity'].plot(data.axis_x, data.axis_hum)
        myplot['rain'].plot(data.axis_x, data.axis_rain)
        myplot['temperature'].plot(data.axis_x, data.axis_temp)
        myplot['light'].plot(data.axis_x, data.axis_light)
        myplot['air_pressure'].plot(data.axis_x, data.axis_pres)
        
    except ValueError as e:
        print(f"Failed to parse payload: {payload}, error: {e}")

if __name__ == "__main__":
    main()