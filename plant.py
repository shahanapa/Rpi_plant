import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import RPi.GPIO as GPIO
import math

k= 1.0

# Configure the ADS1115 and create analog input objects
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 2/3
ph_chan = AnalogIn(ads, ADS.P0)
tds_chan = AnalogIn(ads, ADS.P1)
temp_channel = AnalogIn(ads, ADS.P2)

# Set up GPIO for TDS sensor
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27,GPIO.OUT)
GPIO.setup(22,GPIO.OUT)
GPIO.output(17, GPIO.LOW)

# Set limit values
ph_limit = [6, 8]
tds_limit = [400, 450]
conductivity_limit = [250, 650]
temp_limit = [28,32]

# Function to read pH sensor
def read_ph():
    # Get pH sensor reading and convert to pH value
    ph_raw = ph_chan.voltage
    ph=(-5.07*ph_raw)+21.55509299
    temp_voltage = temp_channel.voltage
    temp_range = ((temp_voltage - 0.5) * 100)
    temp_celsius = temp_range / 10

    return ph,temp_celsius

# Function to read TDS sensor
def read_tds():
    # Send pulse to TDS sensor
    GPIO.output(17, GPIO.HIGH)
    time.sleep(0.01)
    GPIO.output(17, GPIO.LOW)

    # Get TDS sensor reading and convert to TDS value
    tds_raw = tds_chan.voltage
    #tds = 1000 * (133.42 * math.exp(6.185 * tds_raw) -0.5)
    #voltage = tds_chan.voltage*5/1024.0
    tds = (((133.42/tds_chan.voltage*tds_chan.voltage*tds_chan.voltage-255.86*tds_chan.voltage*tds_chan.voltage+857.39*tds_chan.voltage)*5)/10)
    return tds

def calc_conductivity(tds_value):
    conductivity = (tds_chan.voltage)*0.5  # convert ppm to mS/cm
    return conductivity

# Main loop to read sensors and print values
while True:
    ph,temp_celsius = read_ph()
    tds = read_tds()
    tds_value = read_tds()
    conductivity = calc_conductivity(tds_value)
   
    # Check if any limit is exceeded and turn on the relay
    if (ph < ph_limit[0] or ph > ph_limit[1] and
        tds < tds_limit[0] or tds > tds_limit[1] and
        conductivity < conductivity_limit[0] or conductivity > conductivity_limit[1] and
        temp_celsius < temp_limit[0] or temp_celsius > temp_limit[1]):
        GPIO.output(22, GPIO.HIGH)
        GPIO.output(27,GPIO.LOW)
        print("pH:", round(ph,2),", Temperature: ",round(temp_celsius,2),", TDS:", round(tds)," ppm,","Conductivity %.2f µS/cm" % conductivity)
        print("Open value 1,Close value 2!")
        time.sleep(2)
    else:
        GPIO.output(22,GPIO.LOW)
        GPIO.output(27, GPIO.HIGH)
        print("pH:", round(ph,2),", Temperature: ",round(temp_celsius,2), ", TDS:", round(tds),"ppm,","Conductivity %.2f mS/cm" % conductivity)
        print("Open value 2,Close value 1!")
        time.sleep(2)
