#!/usr/bin/python

import logging
import BlynkLib
import time
from Adafruit_BME280 import *
import Adafruit_DHT

logging.basicConfig()
bme = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
dht = Adafruit_DHT.DHT11
pin = 4
blynk = BlynkLib.Blynk('faff44d587fe4c5c8d210f0cfde07ac0','192.168.1.100', 8181)

sumCelsiuses, sumHumidity, sumPressure = 0.0, 0.0, 0.0
countMeasurements, countPressure = 0, 0

def get_humidity_temperature():
    for i in range(10):
        humidity, temperature = Adafruit_DHT.read(dht, pin)
        if humidity is not None and humidity > 20 and humidity < 100 and temperature is not None:
           return (humidity, temperature)
        time.sleep(0.1)
    return (-1, -100)
 
@blynk.VIRTUAL_READ(0)
def v0_read_handler():
    celsiuses = bme.read_temperature()
    print u'Temp      = {0:0.2f} \xb0C'.encode('utf8').format(celsiuses)
    blynk.virtual_write(0, round(celsiuses, 1))

@blynk.VIRTUAL_READ(1)
def v1_read_handler():
    humidity, temperature = get_humidity_temperature()

    if humidity > 0:
    	print 'Humidity  = {0:0.2f} %'.format(humidity)
    else:
	print 'Error reading DHT sensor'

    blynk.virtual_write(1, round(humidity))

@blynk.VIRTUAL_READ(2)
def v2_read_handler():
    pascals = bme.read_pressure()
    mmHg = pascals * 0.007501
    print 'Pressure  = {0:0.2f} mmHg'.format(mmHg)
    blynk.virtual_write(2, round(mmHg))

def read_sensors():
    global countMeasurements, sumCelsiuses, sumHumidity, countPressure, sumPressure

    if countMeasurements < 5:
	humidity, celsiuses = get_humidity_temperature()
	if humidity > 0:
	   sumHumidity = sumHumidity + humidity
	   sumCelsiuses = sumCelsiuses + celsiuses
	   countMeasurements = countMeasurements + 1
	else:
	   print 'Error reading DHT sensor'
    else:
	avgCelsiuses = sumCelsiuses/countMeasurements
	print u'Avg Temp      = {0:0.2f} \xb0C'.encode('utf8').format(avgCelsiuses)
    	blynk.virtual_write(0, round(avgCelsiuses, 1))
	avgHumidity = sumHumidity/countMeasurements
	print 'Avg Humidity  = {0:0.2f} %'.format(avgHumidity)
	blynk.virtual_write(1, round(avgHumidity))
	sumCelsiuses = 0.0
	sumHumidity = 0.0
	countMeasurements = 0

    if countPressure < 5:
	sumPressure = sumPressure + bme.read_pressure()
	countPressure = countPressure + 1
    else:
	avgMmHg = (sumPressure/countPressure) * 0.007501
	print 'Avg Pressure  = {0:0.2f} mmHg'.format(avgMmHg)
    	blynk.virtual_write(2,  round(avgMmHg))
	sumPressure = 0.0
	countPressure = 0

blynk.set_user_task(read_sensors, 10000)
blynk.run()


