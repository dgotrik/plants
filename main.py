import time
import RPi.GPIO as GPIO
#import smbus2 as smbus
import json
import PCF8591 as ADC
import Adafruit_BMP.BMP085 as BMP085
import datetime
from dateutil import tz

DEVICE_BUS = 1
ADC_ADDRESS = 0x48
BAROMETER_ADDRESS = 0x77

VOUT_MOISTURE_1 = 33
VOUT_ADC_1 = 29
VOUT_ADC_2 = 23

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(VOUT_MOISTURE_1, GPIO.OUT)
GPIO.setup(VOUT_ADC_1, GPIO.OUT)
# GPIO.setup(VOUT_ADC_2, GPIO.OUT)


GPIO.output(VOUT_MOISTURE_1, GPIO.HIGH)
GPIO.output(VOUT_ADC_1, GPIO.HIGH)
# GPIO.output(VOUT_ADC_2, GPIO.HIGH)

## bus = smbus.SMBus(DEVICE_BUS)

## Activate PCF8591 ADC on I2C bus
## First: ADDRESSING
## 10010000 - 0x90  - XXXX fixed | A2A1A0 | R/!W
## bus.write_byte_data(90)
## Second : CONTROL
## 0 | Analog output active 1 | Analog input: 00 four single-ended inputs
## 0 | Auto-increment 1 | A/D Channel # 00/01/10/11
## 01000100 - 0x44
ADC.setup(ADC_ADDRESS)
baro = BMP085.BMP085() # mode=BMP085.BMP085_ULTRAHIGHRES)


def write_json(data, filename='data.json'):
    with open(filename,'w') as f:
        json.dump(data, f, indent=4)

with open('data.json') as data_file:
    data = json.load(data_file)
    events = data['weather_events']


    while(1):

        print("--------")
        GPIO.output(VOUT_MOISTURE_1, GPIO.HIGH)
        GPIO.output(VOUT_ADC_1, GPIO.HIGH)
        moisture1 = ADC.read(0)
        moisture2 = ADC.read(1)
        light = ADC.read(2)
        humiture = ADC.read(3)
        print("Moisture1 : {0:0.2f}".format(moisture1))
        print("Moisture2 : {0:0.2f}".format(moisture2))
        print("Light Level: {0:0.2f}".format(light))
        print("Humidity: {0:0.2f}".format(humiture))
        GPIO.output(VOUT_MOISTURE_1, GPIO.LOW)

        temp = baro.read_temperature()
        pressure = baro.read_pressure()
        altitude = baro.read_altitude()
        sealevel_pressure = baro.read_sealevel_pressure()
        daytime = datetime.datetime.now(tz.gettz('MDT')).ctime()
        print("Temp = {0:0.2f} *C".format(temp))
        temp = (temp*1.8) + 32
        print("Temp = {0:0.2f} *F".format(temp))
        print("Pressure = {0:0.2f} Pa".format(baro.read_pressure()))
        print("Altitude = {0:0.2f} m".format(baro.read_altitude()))
        print("Sealevel Pressure = {0:0.2f} Pa".format(baro.read_sealevel_pressure()))


        output = {
            "moisture_1": moisture1,
            "moisture_2": moisture2,
            "light_level": light,
            "humidity": humiture,
            "temp_f": temp,
            "altitude": altitude,
            "pressure": pressure,
            "sealevel_pressure": sealevel_pressure,
            "datetime":daytime
        }

        time.sleep(1)

        json_out = json.dumps(output)
        print(json_out)
        events.append(output)
        write_json(data)
        time.sleep(600)

